"""
系统配置 Pydantic Schemas
负责人: 于凯程
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ConfigBase(BaseModel):
    """配置基础模型"""
    config_key: str = Field(..., max_length=100)
    config_value: str
    category: str = Field(..., max_length=50)
    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    value_type: str = Field("string", max_length=20)


class ConfigCreate(ConfigBase):
    """创建配置的请求模型"""
    is_required: bool = False
    default_value: Optional[str] = None
    validation_rule: Optional[str] = None
    is_active: bool = True
    is_editable: bool = True


class ConfigUpdate(BaseModel):
    """更新配置的请求模型"""
    config_value: Optional[str] = None
    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ConfigRead(ConfigBase):
    """返回配置信息的响应模型"""
    id: int
    is_required: bool
    default_value: Optional[str] = None
    validation_rule: Optional[str] = None
    is_active: bool
    is_editable: bool
    last_modified_by: Optional[int] = None
    last_modified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConfigListItem(BaseModel):
    """配置列表项(精简版)"""
    id: int
    config_key: str
    config_value: str
    category: str
    display_name: Optional[str] = None
    value_type: str
    is_active: bool

    class Config:
        from_attributes = True


class ConfigQueryParams(BaseModel):
    """配置查询参数"""
    category: Optional[str] = None
    is_active: Optional[bool] = None
    search: Optional[str] = Field(None, description="搜索关键字(key或display_name)")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(50, ge=1, le=200, description="每页数量")


class ConfigBatch(BaseModel):
    """批量更新配置"""
    configs: dict = Field(..., description="配置键值对 {key: value}")
