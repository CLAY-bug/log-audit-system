from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# -------------------------------------------
# Shared Properties
# -------------------------------------------
class LogBase(BaseModel):
    """
    日志基础模型，定义创建和读取共用的字段
    """
    source: str = Field(..., min_length=1, max_length=50, description="日志来源 (e.g. nginx, web_app)",
                        example="web_app")
    level: str = Field(..., min_length=1, max_length=20, description="日志级别 (e.g. INFO, ERROR)", example="ERROR")

    # timestamp 可选，如果不传则由后端默认设为当前时间
    timestamp: Optional[datetime] = Field(default=None, description="日志发生时间")

    ip: Optional[str] = Field(None, max_length=50, description="来源IP", example="192.168.1.100")
    user: Optional[str] = Field(None, max_length=100, description="操作用户", example="admin")
    message: str = Field(..., description="日志具体内容", example="User login failed due to bad password")

    raw_data: Optional[str] = Field(None, description="原始日志行数据，用于备份", example='2025-12-10 ERROR ...')


# -------------------------------------------
# Properties to receive on creation
# -------------------------------------------
class LogCreate(LogBase):
    """
    创建日志时的请求体模型
    继承自 LogBase，目前没有额外字段，但保留扩展性
    """
    pass


# -------------------------------------------
# Properties to return to client
# -------------------------------------------
class LogRead(LogBase):
    """
    返回给前端的日志模型
    增加了数据库自动生成的 id 和 created_at
    """
    id: int
    created_at: datetime

    class Config:
        # 允许从 ORM 对象读取数据 (适配 SQLAlchemy)
        # Pydantic V2 使用 from_attributes = True
        # Pydantic V1 使用 orm_mode = True
        orm_mode = True
        from_attributes = True


# -------------------------------------------
# Helper Schemas
# -------------------------------------------
class LogSearchResults(BaseModel):
    """
    日志分页查询的返回结构
    """
    total: int
    results: List[LogRead]


# 注意：查询参数 (QueryParams) 通常不作为 Pydantic Model 放在 Body 里，
# 而是作为 Depends 类放在 api/deps.py 或 endpoints/logs.py 中。
# 但为了对应你的分工表，我们可以定义一个简单的类用于类型提示，
# 或者如果你们决定用 POST 做复杂的查询筛选，则可以使用这个 Model。
class LogFilter(BaseModel):
    """
    复杂筛选条件模型
    """
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    level: Optional[str] = None
    source: Optional[str] = None
    keyword: Optional[str] = None
    ip: Optional[str] = None