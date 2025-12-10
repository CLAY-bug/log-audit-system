from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field


# ============================================================
# 一、日志公共字段模型
# ============================================================

class LogBase(BaseModel):
    """
    日志基础模型（在“创建”和“读取”场景下都通用的业务字段）

    注意：
    - 不包含数据库自动生成的字段：id、created_at
    - 字段需要和 models.Log 中的列保持一一对应：
      source, level, timestamp, ip, user, message, raw_data
    """

    source: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="日志来源，例如：nginx、web_app、system、firewall 等。"
                    "用于区分不同系统/模块产生的日志，前端筛选时也会用到。",
        example="web_app",
    )

    level: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="日志级别，例如：DEBUG、INFO、WARN、ERROR 等。",
        example="ERROR",
    )

    # 这里定义为 Optional：
    # - 如果调用方能提供“日志原始时间”，推荐传入；
    # - 如果不传，由后端在 CRUD 层兜底填充为当前时间或从 raw_data 中解析；
    #   这样既方便使用，又能保证数据库中 timestamp 字段非空。
    timestamp: Optional[datetime] = Field(
        default=None,
        description="日志发生时间（以日志内容为准，而非入库时间）。"
                    "如果调用方不传，后端可以默认使用当前时间。",
        example="2025-12-10T12:34:56",
    )

    ip: Optional[str] = Field(
        None,
        max_length=50,
        description="产生该日志的来源 IP 地址，支持 IPv4 / IPv6 字符串。"
                    "如果日志中无法提取 IP，可以为空。",
        example="192.168.1.100",
    )

    user: Optional[str] = Field(
        None,
        max_length=100,
        description="与该日志相关的操作用户，例如：admin、user_123。"
                    "如果日志中无法解析出用户，可以为空。",
        example="admin",
    )

    message: str = Field(
        ...,
        description="日志的主要内容/摘要，用于前端列表展示和关键字搜索。",
        example="User login failed due to bad password",
    )

    raw_data: Optional[str] = Field(
        None,
        description="原始日志行数据（完整文本或 JSON 字符串），用于备份和排障。"
                    "例如：'2025-12-10 12:34:56 ERROR web_app ...'",
        example="2025-12-10 12:34:56 ERROR web_app User login failed ...",
    )


# ============================================================
# 二、创建日志时的请求体模型
# ============================================================

class LogCreate(LogBase):
    """
    创建日志时的请求体模型（POST /logs）

    说明：
    - 目前直接继承 LogBase，没有新增字段；
    - 如果未来需要区分“对外开放的创建接口”和“内部采集接口”，
      可以在这里新增一些内部使用字段。
    """
    pass


# ============================================================
# 三、更新日志时的请求体模型（可选使用）
# ============================================================

class LogUpdate(BaseModel):
    """
    更新日志时的请求体模型（PUT /logs/{id} 或 PATCH /logs/{id}）

    说明：
    - 当前系统如果不提供“修改日志”的接口，可以暂时不用该模型；
      但在这里预留，方便将来扩展。
    - 所有字段都为 Optional，表示“只更新请求体中出现的字段”。
    """

    source: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="（可选）新的日志来源。",
        example="web_app",
    )

    level: Optional[str] = Field(
        None,
        min_length=1,
        max_length=20,
        description="（可选）新的日志级别。",
        example="INFO",
    )

    timestamp: Optional[datetime] = Field(
        None,
        description="（可选）新的日志发生时间。",
        example="2025-12-10T12:34:56",
    )

    ip: Optional[str] = Field(
        None,
        max_length=50,
        description="（可选）新的来源 IP 地址。",
        example="10.0.0.1",
    )

    user: Optional[str] = Field(
        None,
        max_length=100,
        description="（可选）新的操作用户。",
        example="operator1",
    )

    message: Optional[str] = Field(
        None,
        description="（可选）新的日志内容摘要。",
        example="Update user profile success",
    )

    raw_data: Optional[str] = Field(
        None,
        description="（可选）新的原始日志数据。",
        example="2025-12-10 13:00:00 INFO web_app Update user profile success ...",
    )


# ============================================================
# 四、单条日志的返回模型（对外返回）
# ============================================================

class LogRead(LogBase):
    """
    返回给前端的日志模型（单条日志记录）

    说明：
    - 在 LogBase 的基础上增加：
      - id: 主键 ID
      - created_at: 入库时间
    - 常用于：
      - GET /logs/{id} 的响应体；
      - 日志列表中每一条记录的结构。
    """

    id: int = Field(
        ...,
        description="日志主键 ID，由数据库自增生成。",
        example=1,
    )

    created_at: datetime = Field(
        ...,
        description="日志记录写入数据库的时间（入库时间）。",
        example="2025-12-10T12:35:00",
    )

    class Config:
        # 允许 Pydantic 从 ORM 对象（如 SQLAlchemy 模型实例）中读取属性。
        # - 在 Pydantic v1 中使用 orm_mode = True
        # - 在 Pydantic v2 中使用 from_attributes = True
        orm_mode = True
        from_attributes = True


# ============================================================
# 五、日志列表分页结果模型
# ============================================================

class LogSearchResults(BaseModel):
    """
    日志分页查询的返回结构（列表接口统一返回格式）

    典型使用场景：
    - GET /logs
    - POST /logs/search

    返回示例：
    {
      "total": 132,
      "page": 2,
      "page_size": 20,
      "results": [ {单条日志数据}, ... ]
    }
    """

    total: int = Field(
        ...,
        description="满足当前查询条件的日志总条数。",
        example=132,
    )

    page: int = Field(
        ...,
        description="当前页码（从 1 开始）。"
                    "通常与请求参数中的 page 一致，便于前端做分页显示。",
        example=2,
    )

    page_size: int = Field(
        ...,
        description="当前页请求的条数（每页大小）。"
                    "通常与请求参数中的 page_size 一致。",
        example=20,
    )

    results: List[LogRead] = Field(
        ...,
        description="当前页的日志记录列表，每一项为一条完整的日志数据。",
    )


# ============================================================
# 六、复杂筛选条件模型（可用于 Query 或 Body）
# ============================================================

class LogFilter(BaseModel):
    """
    复杂筛选条件模型

    用法一（推荐）：
    - 在 GET /logs 中作为 Depends 使用，从查询字符串中解析参数：
        @router.get("/logs", response_model=LogSearchResults)
        async def list_logs(filter: LogFilter = Depends()):
            ...

    用法二：
    - 在 POST /logs/search 中作为请求体，用于前端提交更复杂的筛选条件。
    """

    start_time: Optional[datetime] = Field(
        None,
        description="时间范围过滤的起始时间（包含）。如果为空则不限制起始时间。",
        example="2025-12-10T00:00:00",
    )

    end_time: Optional[datetime] = Field(
        None,
        description="时间范围过滤的结束时间（通常为包含）。如果为空则不限制结束时间。",
        example="2025-12-10T23:59:59",
    )

    # 单一日志级别过滤
    level: Optional[str] = Field(
        None,
        description="按单个日志级别进行过滤，例如：'ERROR'。",
        example="ERROR",
    )

    # 多个日志级别过滤（高优先级）
    levels: Optional[List[str]] = Field(
        None,
        description="按多个日志级别进行过滤，例如：['ERROR', 'WARN']。"
                    "如果同时提供 level 和 levels，建议以 levels 为准。",
        example=["ERROR", "WARN"],
    )

    source: Optional[str] = Field(
        None,
        description="按日志来源过滤，例如：'nginx'、'web_app'。",
        example="nginx",
    )

    ip: Optional[str] = Field(
        None,
        description="按来源 IP 精确匹配过滤。",
        example="192.168.1.100",
    )

    user: Optional[str] = Field(
        None,
        description="按操作用户过滤，例如：admin、user_123。",
        example="admin",
    )

    keyword: Optional[str] = Field(
        None,
        description="关键字模糊搜索，一般用于在 message 或 raw_data 字段上做 LIKE 查询。",
        example="login failed",
    )

    page: int = Field(
        1,
        ge=1,
        description="分页参数：页码，从 1 开始。默认第 1 页。",
        example=1,
    )

    page_size: int = Field(
        20,
        ge=1,
        le=500,
        description="分页参数：每页返回的日志条数。默认 20，最大 500。",
        example=20,
    )
