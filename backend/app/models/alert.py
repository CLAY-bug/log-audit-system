"""
告警模型 - Alerts Table ORM Definition
负责人: 于凯程
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.base import Base


class AlertLevel(str, enum.Enum):
    """告警级别枚举"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(str, enum.Enum):
    """告警类型枚举"""
    BRUTE_FORCE = "BRUTE_FORCE"  # 暴力破解
    ERROR_LOG = "ERROR_LOG"  # 错误日志
    SUSPICIOUS_ACCESS = "SUSPICIOUS_ACCESS"  # 可疑访问
    SYSTEM_ANOMALY = "SYSTEM_ANOMALY"  # 系统异常
    CUSTOM = "CUSTOM"  # 自定义


class AlertStatus(str, enum.Enum):
    """告警状态枚举"""
    UNHANDLED = "UNHANDLED"  # 未处理
    HANDLING = "HANDLING"  # 处理中
    RESOLVED = "RESOLVED"  # 已解决
    IGNORED = "IGNORED"  # 已忽略


class Alert(Base):
    """
    告警表模型

    用于存储系统产生的各类安全告警信息
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, comment="告警ID")

    # 告警基本信息
    alert_type = Column(
        SQLEnum(AlertType),
        nullable=False,
        index=True,
        comment="告警类型"
    )
    alert_level = Column(
        SQLEnum(AlertLevel),
        nullable=False,
        default=AlertLevel.MEDIUM,
        index=True,
        comment="告警级别"
    )
    title = Column(String(200), nullable=False, comment="告警标题")
    description = Column(Text, nullable=False, comment="告警详细描述")

    # 关联信息
    related_ip = Column(String(50), index=True, comment="关联IP地址")
    related_user = Column(String(100), index=True, comment="关联用户")
    related_log_ids = Column(Text, comment="关联日志ID列表(JSON格式)")

    # 告警统计信息
    trigger_count = Column(
        Integer,
        default=1,
        comment="触发次数(同类告警可能多次触发)"
    )

    # 状态管理
    status = Column(
        SQLEnum(AlertStatus),
        nullable=False,
        default=AlertStatus.UNHANDLED,
        index=True,
        comment="告警状态"
    )
    handler_user_id = Column(Integer, comment="处理人用户ID")
    handler_note = Column(Text, comment="处理备注")
    handled_at = Column(DateTime, comment="处理时间")

    # 时间戳
    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        index=True,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 额外数据(JSON格式，存储规则特定的详细信息)
    extra_data = Column(Text, comment="额外数据(JSON)")

    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, level={self.alert_level}, status={self.status})>"
