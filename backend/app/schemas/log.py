from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum

# =========================
# 日志来源的枚举类型
# =========================

class LogSourceEnum(str, Enum):
    """
    日志来源枚举，用于校验前端提交的日志来源字段
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

class LogLevelEnum(str, Enum):
    """
    日志级别枚举，用于校验前端提交的日志级别字段
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"

# =========================
# 日志接入方式的枚举类型
# =========================

class LogIngestTypeEnum(str, Enum):
    """
    日志接入方式枚举，用于校验前端提交的日志接入方式字段
    """
    FILE = "file"
    API = "api"
    MANUAL = "manual"

# =========================
# 日志解析状态的枚举类型
# =========================

class LogParseStatusEnum(str, Enum):
    """
    日志解析状态枚举，用于校验前端提交的解析状态字段
    """
    OK = "ok"
    FAILED = "failed"

# =========================
# 日志基础模型
# =========================

class LogBase(BaseModel):
    """
    日志基础模型，包含创建和读取时共享的字段
    """
    source: LogSourceEnum = Field(..., description="日志来源：如 WEB_APP、NETWORK 等")
    level: LogLevelEnum = Field(..., description="日志级别：如 INFO、ERROR 等")
    timestamp: datetime = Field(..., description="日志发生时间")
    ip: Optional[str] = Field(None, description="日志来源的 IP 地址")
    user_name: Optional[str] = Field(None, description="日志中的用户名")
    message: str = Field(..., description="日志内容")
    raw_data: Optional[str] = Field(None, description="原始日志数据")

# =========================
# 创建日志请求体
# =========================

class LogCreate(LogBase):
    """
    创建日志时的请求体模型
    """
    pass

# =========================
# 返回日志详情（包含数据库生成的字段）
# =========================

class LogRead(LogBase):
    """
    返回给前端的日志详情模型，包含数据库自动生成的字段
    """
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# =========================
# 日志分页查询结果模型
# =========================

class LogSearchResults(BaseModel):
    """
    日志分页查询结果模型，包含分页信息和日志列表
    """
    total: int
    page: int
    page_size: int
    results: List[LogRead]

# =========================
# 日志查询过滤条件模型
# =========================

class LogFilter(BaseModel):
    """
    日志查询过滤条件模型，用于支持各种筛选条件
    """
    start_time: Optional[datetime] = Field(None, description="起始时间，用于按时间范围过滤")
    end_time: Optional[datetime] = Field(None, description="结束时间，用于按时间范围过滤")
    levels: Optional[List[LogLevelEnum]] = Field(None, description="日志级别的过滤，多选")
    source: Optional[LogSourceEnum] = Field(None, description="日志来源的过滤")
    keyword: Optional[str] = Field(None, description="日志内容的关键字搜索")
    ip: Optional[str] = Field(None, description="按 IP 地址过滤")
    ingest_type: Optional[LogIngestTypeEnum] = Field(None, description="日志接入方式的过滤")
    parse_status: Optional[LogParseStatusEnum] = Field(None, description="日志解析状态的过滤")
    page: int = Field(1, description="当前页，默认第 1 页")
    page_size: int = Field(20, description="每页返回的日志条数，默认 20 条")

