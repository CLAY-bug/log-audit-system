"""
操作日志记录器服务 - Operation Logger Service
负责人: 于凯程

提供统一的操作日志记录功能
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.operation_log import OperationLog


class OperationLogger:
    """操作日志记录器"""

    # 操作类型常量
    class Actions:
        # 认证相关
        LOGIN = "LOGIN"
        LOGOUT = "LOGOUT"
        LOGIN_FAILED = "LOGIN_FAILED"

        # 日志相关
        UPLOAD_LOG = "UPLOAD_LOG"
        DELETE_LOG = "DELETE_LOG"
        EXPORT_LOG = "EXPORT_LOG"
        QUERY_LOG = "QUERY_LOG"

        # 告警相关
        UPDATE_ALERT_STATUS = "UPDATE_ALERT_STATUS"
        CREATE_ALERT = "CREATE_ALERT"
        DELETE_ALERT = "DELETE_ALERT"

        # 配置相关
        UPDATE_CONFIG = "UPDATE_CONFIG"
        CREATE_CONFIG = "CREATE_CONFIG"
        DELETE_CONFIG = "DELETE_CONFIG"

        # 用户管理
        CREATE_USER = "CREATE_USER"
        UPDATE_USER = "UPDATE_USER"
        DELETE_USER = "DELETE_USER"
        CHANGE_PASSWORD = "CHANGE_PASSWORD"

    # 资源类型常量
    class Resources:
        USER = "user"
        LOG = "log"
        ALERT = "alert"
        CONFIG = "config"
        SYSTEM = "system"

    def __init__(self, db: Session):
        self.db = db

    def record(
            self,
            user_id: int,
            username: str,
            action: str,
            detail: str,
            ip_address: Optional[str] = None,
            user_agent: Optional[str] = None,
            request_url: Optional[str] = None,
            request_method: Optional[str] = None,
            resource_type: Optional[str] = None,
            resource_id: Optional[str] = None,
            result: str = "SUCCESS",
            extra_data: Optional[str] = None
    ) -> OperationLog:
        """
        记录操作日志

        Args:
            user_id: 操作用户ID
            username: 操作用户名
            action: 操作类型
            detail: 操作详情描述
            ip_address: 来源IP
            user_agent: 用户代理
            request_url: 请求URL
            request_method: 请求方法
            resource_type: 资源类型
            resource_id: 资源ID
            result: 操作结果(SUCCESS/FAILED)
            extra_data: 额外数据(JSON)

        Returns:
            操作日志对象
        """
        operation_log = OperationLog(
            user_id=user_id,
            username=username,
            action=action,
            detail=detail,
            ip_address=ip_address,
            user_agent=user_agent,
            request_url=request_url,
            request_method=request_method,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            extra_data=extra_data
        )

        self.db.add(operation_log)
        self.db.commit()
        self.db.refresh(operation_log)

        return operation_log


def record_operation(
        db: Session,
        user_id: int,
        username: str,
        action: str,
        detail: str,
        **kwargs
) -> OperationLog:
    """
    记录操作日志的便捷函数

    在各个接口中调用此函数记录操作

    Args:
        db: 数据库会话
        user_id: 用户ID
        username: 用户名
        action: 操作类型
        detail: 操作详情
        **kwargs: 其他参数(ip_address, user_agent等)

    Returns:
        操作日志对象

    Example:
        >>> record_operation(
        ...     db,
        ...     user_id=1,
        ...     username="admin",
        ...     action=OperationLogger.Actions.LOGIN,
        ...     detail="用户登录成功",
        ...     ip_address="192.168.1.100"
        ... )
    """
    logger = OperationLogger(db)
    return logger.record(user_id, username, action, detail, **kwargs)


# 预定义的操作日志模板
class OperationTemplates:
    """操作日志消息模板"""

    @staticmethod
    def login(username: str, ip: str) -> str:
        return f"用户 {username} 从 {ip} 登录系统"

    @staticmethod
    def logout(username: str) -> str:
        return f"用户 {username} 退出系统"

    @staticmethod
    def login_failed(username: str, ip: str, reason: str = "") -> str:
        return f"用户 {username} 从 {ip} 登录失败" + (f": {reason}" if reason else "")

    @staticmethod
    def upload_log(filename: str, count: int) -> str:
        return f"上传日志文件 {filename}，解析成功 {count} 条"

    @staticmethod
    def export_log(count: int, filters: str = "") -> str:
        base = f"导出 {count} 条日志"
        return base + (f"，筛选条件: {filters}" if filters else "")

    @staticmethod
    def update_alert_status(alert_id: int, old_status: str, new_status: str) -> str:
        return f"修改告警 #{alert_id} 状态: {old_status} -> {new_status}"

    @staticmethod
    def update_config(key: str, old_value: str, new_value: str) -> str:
        return f"修改配置 {key}: {old_value} -> {new_value}"

    @staticmethod
    def create_user(username: str, role: str) -> str:
        return f"创建用户 {username}，角色: {role}"

    @staticmethod
    def delete_user(username: str) -> str:
        return f"删除用户 {username}"
