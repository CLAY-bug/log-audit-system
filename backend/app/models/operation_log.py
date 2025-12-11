"""
操作日志模型 - Operation Log Table ORM Definition
负责人: 于凯程
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from datetime import datetime

from app.db.base import Base


class OperationLog(Base):
    """
    操作日志表模型

    用于记录系统用户的所有关键操作，便于审计追踪
    """
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True, comment="操作日志ID")

    # 操作用户信息
    user_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="操作用户ID"
    )
    username = Column(String(100), nullable=False, comment="操作用户名")

    # 操作信息
    action = Column(
        String(100),
        nullable=False,
        index=True,
        comment="操作类型(LOGIN/LOGOUT/UPLOAD_LOG/DELETE_LOG/CHANGE_CONFIG/UPDATE_ALERT等)"
    )
    resource_type = Column(
        String(50),
        index=True,
        comment="操作的资源类型(user/log/alert/config等)"
    )
    resource_id = Column(String(100), comment="操作的资源ID")

    # 操作详情
    detail = Column(Text, comment="操作详细描述")
    result = Column(
        String(20),
        default="SUCCESS",
        comment="操作结果(SUCCESS/FAILED)"
    )

    # 请求信息
    ip_address = Column(String(50), index=True, comment="操作来源IP")
    user_agent = Column(String(500), comment="用户代理(浏览器信息)")
    request_url = Column(String(500), comment="请求URL")
    request_method = Column(String(10), comment="请求方法(GET/POST/PUT/DELETE等)")

    # 时间戳
    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        index=True,
        comment="操作时间"
    )

    # 额外数据(JSON格式)
    extra_data = Column(Text, comment="额外数据(JSON格式)")

    def __repr__(self):
        return f"<OperationLog(id={self.id}, user={self.username}, action={self.action})>"
