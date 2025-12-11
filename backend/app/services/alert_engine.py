"""
告警引擎服务 - Alert Engine Service
负责人: 于凯程

实现各类告警规则的检测和触发逻辑
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import json

from app.models.alert import Alert, AlertType, AlertLevel, AlertStatus
from app.models.log import Log
from app.models.config import SystemConfig, ConfigKeys


class AlertEngine:
    """告警引擎"""

    def __init__(self, db: Session):
        self.db = db

    def check_all_rules(self, log_id: Optional[int] = None) -> List[Alert]:
        """
        检查所有告警规则

        Args:
            log_id: 新插入的日志ID(可选)

        Returns:
            生成的告警列表
        """
        alerts = []

        # 规则1: 暴力破解检测
        brute_force_alerts = self.check_brute_force_attack(log_id)
        alerts.extend(brute_force_alerts)

        # 规则2: ERROR日志告警
        if log_id:
            error_alert = self.check_error_log(log_id)
            if error_alert:
                alerts.append(error_alert)

        # 规则3: 可疑访问检测(可扩展)
        # suspicious_alerts = self.check_suspicious_access()
        # alerts.extend(suspicious_alerts)

        return alerts

    def check_brute_force_attack(self, log_id: Optional[int] = None) -> List[Alert]:
        """
        检测暴力破解攻击

        规则: 在N分钟内，来自同一IP的登录失败次数超过阈值

        Args:
            log_id: 新插入的日志ID

        Returns:
            告警列表
        """
        alerts = []

        # 获取配置参数
        threshold = self._get_config_int(
            ConfigKeys.ALERT_BRUTE_FORCE_THRESHOLD,
            default=5
        )
        window_minutes = self._get_config_int(
            ConfigKeys.ALERT_BRUTE_FORCE_WINDOW,
            default=5
        )

        # 计算时间窗口
        time_threshold = datetime.now() - timedelta(minutes=window_minutes)

        # 查询登录失败的日志，按IP分组统计
        # 假设登录失败日志的message包含"login failed"或"authentication failed"
        failed_login_query = self.db.query(
            Log.ip,
            func.count(Log.id).label('fail_count'),
            func.group_concat(Log.id).label('log_ids')
        ).filter(
            and_(
                Log.timestamp >= time_threshold,
                Log.level == "ERROR",
                Log.message.like('%login%failed%') | Log.message.like('%authentication%failed%')
            )
        ).group_by(Log.ip).having(
            func.count(Log.id) >= threshold
        )

        failed_attempts = failed_login_query.all()

        for attempt in failed_attempts:
            ip = attempt.ip
            fail_count = attempt.fail_count
            log_ids = attempt.log_ids

            # 检查是否已存在未处理的同类告警
            existing_alert = self.db.query(Alert).filter(
                and_(
                    Alert.alert_type == AlertType.BRUTE_FORCE,
                    Alert.related_ip == ip,
                    Alert.status.in_([AlertStatus.UNHANDLED, AlertStatus.HANDLING]),
                    Alert.created_at >= time_threshold
                )
            ).first()

            if existing_alert:
                # 更新已存在的告警
                existing_alert.trigger_count += 1
                existing_alert.description = (
                    f"检测到来自IP {ip} 的暴力破解尝试，"
                    f"在过去{window_minutes}分钟内登录失败{fail_count}次，"
                    f"已累计触发{existing_alert.trigger_count}次"
                )
                existing_alert.related_log_ids = log_ids
                existing_alert.updated_at = datetime.now()
                self.db.commit()
            else:
                # 创建新告警
                alert = Alert(
                    alert_type=AlertType.BRUTE_FORCE,
                    alert_level=AlertLevel.HIGH if fail_count >= threshold * 2 else AlertLevel.MEDIUM,
                    title=f"检测到暴力破解攻击 - IP: {ip}",
                    description=(
                        f"检测到来自IP {ip} 的暴力破解尝试，"
                        f"在过去{window_minutes}分钟内登录失败{fail_count}次"
                    ),
                    related_ip=ip,
                    related_log_ids=log_ids,
                    status=AlertStatus.UNHANDLED,
                    extra_data=json.dumps({
                        "fail_count": fail_count,
                        "time_window_minutes": window_minutes,
                        "threshold": threshold
                    })
                )
                self.db.add(alert)
                self.db.commit()
                self.db.refresh(alert)
                alerts.append(alert)

        return alerts

    def check_error_log(self, log_id: int) -> Optional[Alert]:
        """
        检测ERROR级别日志并生成告警

        规则: 所有ERROR级别的日志自动生成告警

        Args:
            log_id: 日志ID

        Returns:
            告警对象或None
        """
        # 检查是否启用ERROR日志告警
        enabled = self._get_config_bool(
            ConfigKeys.ALERT_ERROR_LOG_ENABLED,
            default=True
        )

        if not enabled:
            return None

        # 获取日志记录
        log = self.db.query(Log).filter(Log.id == log_id).first()
        if not log or log.level != "ERROR":
            return None

        # 创建告警
        alert = Alert(
            alert_type=AlertType.ERROR_LOG,
            alert_level=AlertLevel.MEDIUM,
            title=f"ERROR日志告警 - {log.source}",
            description=f"系统检测到ERROR级别日志: {log.message[:200]}",
            related_ip=log.ip,
            related_user=log.user,
            related_log_ids=str(log_id),
            status=AlertStatus.UNHANDLED,
            extra_data=json.dumps({
                "log_id": log_id,
                "log_source": log.source,
                "log_level": log.level
            })
        )

        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        return alert

    def check_suspicious_access(self) -> List[Alert]:
        """
        检测可疑访问行为(可扩展)

        例如:
        - 同一用户短时间内从多个IP登录
        - 访问敏感资源的异常行为
        - 非工作时间的大量操作

        Returns:
            告警列表
        """
        # 此处可以实现更多复杂的检测规则
        # 示例:检测同一用户30分钟内从超过3个不同IP登录
        alerts = []

        time_threshold = datetime.now() - timedelta(minutes=30)

        multi_ip_users = self.db.query(
            Log.user,
            func.count(func.distinct(Log.ip)).label('ip_count'),
            func.group_concat(func.distinct(Log.ip)).label('ip_list')
        ).filter(
            and_(
                Log.timestamp >= time_threshold,
                Log.user.isnot(None),
                Log.message.like('%login%success%')
            )
        ).group_by(Log.user).having(
            func.count(func.distinct(Log.ip)) > 3
        ).all()

        for record in multi_ip_users:
            user = record.user
            ip_count = record.ip_count
            ip_list = record.ip_list

            # 检查是否已存在告警
            existing_alert = self.db.query(Alert).filter(
                and_(
                    Alert.alert_type == AlertType.SUSPICIOUS_ACCESS,
                    Alert.related_user == user,
                    Alert.status.in_([AlertStatus.UNHANDLED, AlertStatus.HANDLING]),
                    Alert.created_at >= time_threshold
                )
            ).first()

            if not existing_alert:
                alert = Alert(
                    alert_type=AlertType.SUSPICIOUS_ACCESS,
                    alert_level=AlertLevel.HIGH,
                    title=f"可疑访问行为 - 用户: {user}",
                    description=(
                        f"用户 {user} 在30分钟内从{ip_count}个不同IP地址登录: {ip_list}"
                    ),
                    related_user=user,
                    status=AlertStatus.UNHANDLED,
                    extra_data=json.dumps({
                        "ip_count": ip_count,
                        "ip_list": ip_list.split(',') if ip_list else []
                    })
                )
                self.db.add(alert)
                self.db.commit()
                self.db.refresh(alert)
                alerts.append(alert)

        return alerts

    def _get_config_int(self, key: str, default: int) -> int:
        """获取整型配置值"""
        config = self.db.query(SystemConfig).filter(
            SystemConfig.config_key == key
        ).first()

        if config and config.is_active:
            try:
                return int(config.config_value)
            except ValueError:
                return default
        return default

    def _get_config_bool(self, key: str, default: bool) -> bool:
        """获取布尔型配置值"""
        config = self.db.query(SystemConfig).filter(
            SystemConfig.config_key == key
        ).first()

        if config and config.is_active:
            return config.config_value.lower() in ('true', '1', 'yes')
        return default


def trigger_alert_check(db: Session, log_id: Optional[int] = None):
    """
    触发告警检查的便捷函数

    在日志插入后调用此函数进行告警检测

    Args:
        db: 数据库会话
        log_id: 新插入的日志ID
    """
    engine = AlertEngine(db)
    return engine.check_all_rules(log_id)
