from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum

# =========================
# 日志来源的枚举类型
# =========================

class LogSourceEnum(enum.Enum):
    """
    日志来源枚举，定义了可能的日志来源类型
    例如：WEB_APP（Web 应用日志）、NETWORK（网络日志）、ROUTER（路由器日志）等
    """
    WEB_APP = "WEB_APP"
    NETWORK = "NETWORK"
    ROUTER = "ROUTER"
    FIREWALL = "FIREWALL"
    DATABASE = "DATABASE"
    OTHER = "OTHER"

# =========================
# 日志级别的枚举类型
# =========================

class LogLevelEnum(enum.Enum):
    """
    日志级别枚举，定义了不同的日志级别
    例如：DEBUG、INFO、WARN、ERROR、FATAL 等
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"

# =========================
# 日志接入方式的枚举类型
# =========================

class LogIngestTypeEnum(enum.Enum):
    """
    日志接入方式枚举，定义了日志的接入方式
    例如：file（文件上传）、api（API 上传）、manual（手动输入）等
    """
    FILE = "file"
    API = "api"
    MANUAL = "manual"

# =========================
# 日志解析状态的枚举类型
# =========================

class LogParseStatusEnum(enum.Enum):
    """
    日志解析状态枚举，定义了日志的解析状态
    例如：ok（解析成功）、failed（解析失败）
    """
    OK = "ok"
    FAILED = "failed"

# =========================
# 日志模型
# =========================

class Log(Base):
    """
    日志模型，定义了日志表 `logs` 的 ORM 结构，映射到数据库中的 logs 表
    """
    __tablename__ = "logs"

    # 主键，自动增长
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 日志来源，使用 ENUM 类型，取值参见 LogSourceEnum
    source = Column(Enum(LogSourceEnum), nullable=False)

    # 日志级别，使用 ENUM 类型，取值参见 LogLevelEnum，默认 INFO
    level = Column(Enum(LogLevelEnum), nullable=False, default=LogLevelEnum.INFO)

    # 原始日志时间，记录日志发生的时间
    timestamp = Column(DateTime, nullable=False)

    # 来源 IP，记录与日志相关的 IP 地址，支持 IPv4/IPv6
    ip = Column(String(45), nullable=True)

    # 日志中的用户名，记录相关的用户名，若无则为空
    user_name = Column(String(64), nullable=True)

    # 日志内容，简要描述日志信息
    message = Column(String(1024), nullable=False)

    # 原始日志数据，保存日志的完整原始文本，便于回溯与解析
    raw_data = Column(Text, nullable=True)

    # 日志接入方式，使用 ENUM 类型，取值参见 LogIngestTypeEnum，默认是文件上传
    ingest_type = Column(Enum(LogIngestTypeEnum), nullable=False, default=LogIngestTypeEnum.FILE)

    # 解析状态，使用 ENUM 类型，取值参见 LogParseStatusEnum，默认解析成功
    parse_status = Column(Enum(LogParseStatusEnum), nullable=False, default=LogParseStatusEnum.OK)

    # 创建时间，记录日志写入数据库的时间
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # 索引设置，提升查询效率
    __table_args__ = (
        # 时间戳索引：便于按时间范围查询
        Index("idx_logs_timestamp", "timestamp"),
        # 日志级别索引：便于按级别查询
        Index("idx_logs_level", "level"),
        # 日志来源索引：便于按来源查询
        Index("idx_logs_source", "source"),
        # IP 索引：便于按 IP 查询
        Index("idx_logs_ip", "ip"),
        # 用户名索引：便于按用户名查询
        Index("idx_logs_user_name", "user_name"),
        # 组合索引：按时间、来源和级别组合查询
        Index("idx_logs_timestamp_source_level", "timestamp", "source", "level"),
    )

    def __repr__(self):
        """
        日志对象的字符串表示，便于调试时查看
        """
        return f"<Log id={self.id}, source={self.source}, level={self.level}, timestamp={self.timestamp}>"
