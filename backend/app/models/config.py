"""
系统配置模型 - System Config Table ORM Definition
负责人: 于凯程
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime

from app.db.base import Base


class SystemConfig(Base):
    """
    系统配置表模型

    用于存储系统级别的配置参数，支持动态修改
    """
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True, comment="配置ID")

    # 配置键值
    config_key = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="配置键(唯一)"
    )
    config_value = Column(Text, nullable=False, comment="配置值")

    # 配置分类
    category = Column(
        String(50),
        nullable=False,
        index=True,
        comment="配置分类(system/log/alert/security等)"
    )

    # 配置元信息
    display_name = Column(String(200), comment="显示名称")
    description = Column(Text, comment="配置描述")
    value_type = Column(
        String(20),
        default="string",
        comment="值类型(string/int/boolean/json等)"
    )

    # 配置验证
    is_required = Column(
        Boolean,
        default=False,
        comment="是否必需配置"
    )
    default_value = Column(Text, comment="默认值")
    validation_rule = Column(Text, comment="验证规则(JSON格式)")

    # 状态控制
    is_active = Column(
        Boolean,
        default=True,
        index=True,
        comment="是否启用"
    )
    is_editable = Column(
        Boolean,
        default=True,
        comment="是否可编辑"
    )

    # 修改记录
    last_modified_by = Column(Integer, comment="最后修改人用户ID")
    last_modified_at = Column(DateTime, comment="最后修改时间")

    # 时间戳
    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    def __repr__(self):
        return f"<SystemConfig(key={self.config_key}, value={self.config_value})>"


# 预定义的配置键常量
class ConfigKeys:
    """系统配置键常量"""
    # 日志相关
    LOG_RETENTION_DAYS = "log_retention_days"  # 日志保留天数
    LOG_MAX_UPLOAD_SIZE = "log_max_upload_size_mb"  # 日志文件最大上传大小(MB)
    LOG_AUTO_PARSE = "log_auto_parse"  # 是否自动解析日志

    # 告警相关
    ALERT_BRUTE_FORCE_THRESHOLD = "alert_brute_force_threshold"  # 暴力破解阈值(次数)
    ALERT_BRUTE_FORCE_WINDOW = "alert_brute_force_window_minutes"  # 暴力破解检测时间窗口(分钟)
    ALERT_ERROR_LOG_ENABLED = "alert_error_log_enabled"  # 是否启用ERROR日志告警
    ALERT_AUTO_RESOLVE_DAYS = "alert_auto_resolve_days"  # 告警自动解决天数

    # 安全相关
    SESSION_TIMEOUT_MINUTES = "session_timeout_minutes"  # 会话超时时间(分钟)
    PASSWORD_MIN_LENGTH = "password_min_length"  # 密码最小长度
    LOGIN_MAX_ATTEMPTS = "login_max_attempts"  # 登录最大尝试次数

    # 系统相关
    SYSTEM_NAME = "system_name"  # 系统名称
    SYSTEM_DESCRIPTION = "system_description"  # 系统描述
    MAINTENANCE_MODE = "maintenance_mode"  # 维护模式
