"""
操作日志查询 API Endpoints
负责人: 于凯程

提供操作日志的查询和统计接口
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional
from datetime import datetime

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.operation_log import OperationLog
from pydantic import BaseModel

router = APIRouter()


class OperationLogRead(BaseModel):
    """操作日志响应模型"""
    id: int
    user_id: int
    username: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    detail: str
    result: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_url: Optional[str] = None
    request_method: Optional[str] = None
    created_at: datetime
    extra_data: Optional[str] = None

    class Config:
        from_attributes = True


class OperationLogListItem(BaseModel):
    """操作日志列表项(精简版)"""
    id: int
    username: str
    action: str
    detail: str
    result: str
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=dict)
def get_operation_logs(
        user_id: Optional[int] = Query(None, description="用户ID"),
        username: Optional[str] = Query(None, description="用户名(模糊搜索)"),
        action: Optional[str] = Query(None, description="操作类型"),
        resource_type: Optional[str] = Query(None, description="资源类型"),
        result: Optional[str] = Query(None, description="操作结果(SUCCESS/FAILED)"),
        ip_address: Optional[str] = Query(None, description="IP地址"),
        start_time: Optional[datetime] = Query(None, description="开始时间"),
        end_time: Optional[datetime] = Query(None, description="结束时间"),
        search: Optional[str] = Query(None, description="搜索关键字(匹配detail)"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    获取操作日志列表

    支持多条件筛选和分页查询

    仅管理员或审计员可以查看所有操作日志
    普通用户只能查看自己的操作日志
    """
    # 构建查询
    query = db.query(OperationLog)

    # 权限控制：普通用户只能看自己的日志
    if current_user.role not in ["admin", "auditor"]:
        query = query.filter(OperationLog.user_id == current_user.id)

    # 应用筛选条件
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    if username:
        query = query.filter(OperationLog.username.like(f"%{username}%"))
    if action:
        query = query.filter(OperationLog.action == action)
    if resource_type:
        query = query.filter(OperationLog.resource_type == resource_type)
    if result:
        query = query.filter(OperationLog.result == result)
    if ip_address:
        query = query.filter(OperationLog.ip_address.like(f"%{ip_address}%"))
    if start_time:
        query = query.filter(OperationLog.created_at >= start_time)
    if end_time:
        query = query.filter(OperationLog.created_at <= end_time)
    if search:
        query = query.filter(OperationLog.detail.like(f"%{search}%"))

    # 统计总数
    total = query.count()

    # 分页查询
    logs = query.order_by(OperationLog.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    # 转换为列表项
    items = [OperationLogListItem.model_validate(log) for log in logs]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/{log_id}", response_model=OperationLogRead)
def get_operation_log_detail(
        log_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    获取操作日志详情
    """
    log = db.query(OperationLog).filter(OperationLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="操作日志不存在")

    # 权限检查：普通用户只能看自己的日志
    if current_user.role not in ["admin", "auditor"]:
        if log.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="权限不足")

    return OperationLogRead.model_validate(log)


@router.get("/stats/actions")
def get_action_stats(
        start_time: Optional[datetime] = Query(None, description="开始时间"),
        end_time: Optional[datetime] = Query(None, description="结束时间"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    按操作类型统计

    返回各操作类型的数量分布
    """
    from sqlalchemy import func

    query = db.query(
        OperationLog.action,
        func.count(OperationLog.id).label('count')
    )

    if start_time:
        query = query.filter(OperationLog.created_at >= start_time)
    if end_time:
        query = query.filter(OperationLog.created_at <= end_time)

    results = query.group_by(OperationLog.action).order_by(
        func.count(OperationLog.id).desc()
    ).all()

    data = [
        {"action": result.action, "count": result.count}
        for result in results
    ]

    return {"data": data}


@router.get("/stats/users")
def get_user_activity_stats(
        start_time: Optional[datetime] = Query(None, description="开始时间"),
        end_time: Optional[datetime] = Query(None, description="结束时间"),
        top_n: int = Query(10, ge=1, le=50, description="返回前N个用户"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    按用户统计操作活跃度

    返回操作最频繁的用户列表
    """
    from sqlalchemy import func

    query = db.query(
        OperationLog.username,
        func.count(OperationLog.id).label('count')
    )

    if start_time:
        query = query.filter(OperationLog.created_at >= start_time)
    if end_time:
        query = query.filter(OperationLog.created_at <= end_time)

    results = query.group_by(OperationLog.username).order_by(
        func.count(OperationLog.id).desc()
    ).limit(top_n).all()

    data = [
        {"username": result.username, "count": result.count}
        for result in results
    ]

    return {"data": data}


@router.delete("/{log_id}")
def delete_operation_log(
        log_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    删除操作日志

    仅管理员可以删除操作日志(谨慎使用)
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")

    log = db.query(OperationLog).filter(OperationLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="操作日志不存在")

    db.delete(log)
    db.commit()

    return {"message": "操作日志删除成功"}
