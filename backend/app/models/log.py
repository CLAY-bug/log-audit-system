from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.db.session import Base  # 假设 Base 定义在 session.py 中，如果是在 base_class.py 请修改引入


class Log(Base):
    """
    日志数据模型
    对应数据库表: logs
    """
    __tablename__ = "logs"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="日志ID")

    # 核心字段 - 需要建立索引以加速查询
    # source: 日志来源 (e.g., "nginx", "web_app", "firewall")
    source = Column(String(50), index=True, nullable=False, comment="日志来源")

    # level: 日志级别 (e.g., "INFO", "WARN", "ERROR")
    level = Column(String(20), index=True, nullable=False, comment="日志级别")

    # timestamp: 日志发生时间 (注意：这可能与入库时间不同，以日志内容为准)
    # 使用 index=True 方便按时间范围查询 (Result filtering by time range)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False, default=func.now(), comment="日志时间")

    # 详细内容
    # ip: 来源 IP 地址 (支持 IPv4/IPv6字符串)
    ip = Column(String(50), nullable=True, index=True, comment="来源IP")

    # user: 操作用户 (e.g., "admin", "user_123")，可选
    user = Column(String(100), nullable=True, comment="操作用户")

    # message: 日志具体内容/摘要
    message = Column(Text, nullable=False, comment="日志内容")

    # 原始数据备份
    # raw_data: 用于存储原始日志行或完整的 JSON 数据，便于后续回溯
    raw_data = Column(Text, nullable=True, comment="原始日志数据")

    # 创建时间 (入库时间)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="入库时间")

    def __repr__(self):
        return f"<Log(id={self.id}, source={self.source}, level={self.level}, time={self.timestamp})>"


"""
    

"""