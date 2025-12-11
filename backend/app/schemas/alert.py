"""
告警 Pydantic Schemas
负责人: 于凯程
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# 枚举定义(与models保持一致)
class AlertLevel(str, Enum):
    """告警级别"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(str, Enum):
    """告警类型"""
    BRUTE_FORCE = "BRUTE_FORCE"
    ERROR_LOG = "ERROR_LOG"
    SUSPICIOUS_ACCESS = "SUSPICIOUS_ACCESS"
    SYSTEM_ANOMALY = "SYSTEM_ANOMALY"
    CUSTOM = "CUSTOM"


class AlertStatus(str, Enum):
    """告警状态"""
    UNHANDLED = "UNHANDLED"
    HANDLING = "HANDLING"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


# 基础Schema
class AlertBase(BaseModel):
    """告警基础模型"""
    alert_type: AlertType
    alert_level: AlertLevel
    title: str = Field(..., max_length=200)
    description: str
    related_ip: Optional[str] = Field(None, max_length=50)
    related_user: Optional[str] = Field(None, max_length=100)
    related_log_ids: Optional[str] = None
    extra_data: Optional[str] = None


class AlertCreate(AlertBase):
    """创建告警的请求模型"""
    trigger_count: Optional[int] = 1


class AlertUpdate(BaseModel):
    """更新告警的请求模型"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    alert_level: Optional[AlertLevel] = None
    extra_data: Optional[str] = None


class AlertUpdateStatus(BaseModel):
    """更新告警状态的请求模型"""
    status: AlertStatus
    handler_note: Optional[str] = None


class AlertRead(AlertBase):
    """返回告警信息的响应模型"""
    id: int
    status: AlertStatus
    trigger_count: int
    handler_user_id: Optional[int] = None
    handler_note: Optional[str] = None
    handled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertListItem(BaseModel):
    """告警列表项(精简版)"""
    id: int
    alert_type: AlertType
    alert_level: AlertLevel
    title: str
    status: AlertStatus
    related_ip: Optional[str] = None
    related_user: Optional[str] = None
    trigger_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class AlertQueryParams(BaseModel):
    """告警查询参数"""
    alert_type: Optional[AlertType] = None
    alert_level: Optional[AlertLevel] = None
    status: Optional[AlertStatus] = None
    related_ip: Optional[str] = None
    related_user: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class AlertStats(BaseModel):
    """告警统计信息"""
    total: int
    unhandled: int
    handling: int
    resolved: int
    ignored: int
    by_level: dict  # {level: count}
    by_type: dict  # {type: count}
