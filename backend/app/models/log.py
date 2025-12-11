from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.db.base import Base  # 根据系统框架说明，Base 定义在 app.db.base 中


class Log(Base):
    """
    日志数据模型
    对应数据库表: logs

    字段设计参考《综合日志分析系统.md》3.3 中的“建议字段”：
    - id: 主键
    - source: 日志来源（如 nginx、app、system）
    - level: 日志级别（INFO/WARN/ERROR 等）
    - timestamp: 日志时间（以日志内容为准）
    - ip: 来源 IP（可选）
    - user: 相关用户名（可选）
    - message: 日志内容（摘要/主要信息）
    - raw_data: 原始日志行（方便回溯， 可选）
    额外增加:
    - created_at: 入库时间（DB 自动填充）
    """

    __tablename__ = "logs"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="日志ID")

    # 日志来源 (e.g., "nginx", "web_app", "firewall")
    source = Column(String(50), index=True, nullable=False, comment="日志来源")

    # 日志级别 (e.g., "INFO", "WARN", "ERROR")
    level = Column(String(20), index=True, nullable=False, comment="日志级别")

    # 日志发生时间（注意：与入库时间不同，以日志内容为准）
    # 不设置默认值，要求解析器/接口显式提供
    timestamp = Column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
        comment="日志时间",
    )

    # 来源 IP 地址 (支持 IPv4/IPv6 字符串)
    ip = Column(String(50), nullable=True, index=True, comment="来源IP")

    # 操作用户 (e.g., "admin", "user_123")，可选
    user = Column(String(100), nullable=True, index=True, comment="操作用户")

    # 日志具体内容/摘要
    message = Column(Text, nullable=False, comment="日志内容")

    # 原始日志数据：原始日志行或完整 JSON，便于回溯/重新解析
    raw_data = Column(Text, nullable=True, comment="原始日志数据")

    # 入库时间（由数据库自动填充）
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="入库时间",
    )

    def __repr__(self) -> str:
        return (
            f"<Log(id={self.id}, source={self.source}, "
            f"level={self.level}, time={self.timestamp})>"
        )
