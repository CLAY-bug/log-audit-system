"""
告警管理 API Endpoints
负责人: 于凯程

提供告警的查询、详情查看、状态更新等接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.alert import Alert, AlertType, AlertLevel, AlertStatus
from app.schemas.alert import (
    AlertRead,
    AlertListItem,
    AlertQueryParams,
    AlertUpdateStatus,
    AlertStats,
    AlertCreate,
    AlertUpdate
)
from app.services.operation_logger import record_operation, OperationLogger, OperationTemplates

router = APIRouter()


@router.get("/", response_model=dict)
def get_alerts(
        alert_type: Optional[AlertType] = None,
        alert_level: Optional[AlertLevel] = None,
        status: Optional[AlertStatus] = None,
        related_ip: Optional[str] = None,
        related_user: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    获取告警列表

    支持多条件筛选和分页
    """
    # 构建查询
    query = db.query(Alert)

    # 应用筛选条件
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if alert_level:
        query = query.filter(Alert.alert_level == alert_level)
    if status:
        query = query.filter(Alert.status == status)
    if related_ip:
        query = query.filter(Alert.related_ip.like(f"%{related_ip}%"))
    if related_user:
        query = query.filter(Alert.related_user.like(f"%{related_user}%"))
    if start_time:
        query = query.filter(Alert.created_at >= start_time)
    if end_time:
        query = query.filter(Alert.created_at <= end_time)

    # 统计总数
    total = query.count()

    # 分页查询
    alerts = query.order_by(Alert.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    # 转换为列表项
    items = [AlertListItem.model_validate(alert) for alert in alerts]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert_detail(
        alert_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    获取告警详情
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="告警不存在")

    return AlertRead.model_validate(alert)


@router.patch("/{alert_id}/status", response_model=AlertRead)
def update_alert_status(
        alert_id: int,
        status_update: AlertUpdateStatus,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    更新告警状态

    允许审计员修改告警的处理状态和备注
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="告警不存在")

    # 记录旧状态
    old_status = alert.status

    # 更新状态
    alert.status = status_update.status
    alert.handler_user_id = current_user.id
    if status_update.handler_note:
        alert.handler_note = status_update.handler_note
    alert.handled_at = datetime.now()
    alert.updated_at = datetime.now()

    db.commit()
    db.refresh(alert)

    # 记录操作日志
    record_operation(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action=OperationLogger.Actions.UPDATE_ALERT_STATUS,
        detail=OperationTemplates.update_alert_status(
            alert_id,
            old_status.value,
            status_update.status.value
        ),
        resource_type=OperationLogger.Resources.ALERT,
        resource_id=str(alert_id)
    )

    return AlertRead.model_validate(alert)


@router.patch("/{alert_id}", response_model=AlertRead)
def update_alert(
        alert_id: int,
        alert_update: AlertUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    更新告警信息

    仅管理员可以修改告警的基本信息
    """
    # 检查管理员权限
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")

    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="告警不存在")

    # 更新字段
    update_data = alert_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)

    alert.updated_at = datetime.now()

    db.commit()
    db.refresh(alert)

    return AlertRead.model_validate(alert)


@router.get("/stats/summary", response_model=AlertStats)
def get_alert_stats(
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    获取告警统计信息

    返回各状态、级别、类型的告警数量统计
    """
    # 基础查询
    query = db.query(Alert)

    if start_time:
        query = query.filter(Alert.created_at >= start_time)
    if end_time:
        query = query.filter(Alert.created_at <= end_time)

    # 总数
    total = query.count()

    # 按状态统计
    unhandled = query.filter(Alert.status == AlertStatus.UNHANDLED).count()
    handling = query.filter(Alert.status == AlertStatus.HANDLING).count()
    resolved = query.filter(Alert.status == AlertStatus.RESOLVED).count()
    ignored = query.filter(Alert.status == AlertStatus.IGNORED).count()

    # 按级别统计
    by_level = {}
    for level in AlertLevel:
        count = query.filter(Alert.alert_level == level).count()
        by_level[level.value] = count

    # 按类型统计
    by_type = {}
    for alert_type in AlertType:
        count = query.filter(Alert.alert_type == alert_type).count()
        by_type[alert_type.value] = count

    return AlertStats(
        total=total,
        unhandled=unhandled,
        handling=handling,
        resolved=resolved,
        ignored=ignored,
        by_level=by_level,
        by_type=by_type
    )


@router.delete("/{alert_id}")
def delete_alert(
        alert_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    删除告警

    仅管理员可以删除告警
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")

    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="告警不存在")

    db.delete(alert)
    db.commit()

    # 记录操作日志
    record_operation(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action=OperationLogger.Actions.DELETE_ALERT,
        detail=f"删除告警 #{alert_id}: {alert.title}",
        resource_type=OperationLogger.Resources.ALERT,
        resource_id=str(alert_id)
    )

    return {"message": "告警删除成功"}


@router.post("/", response_model=AlertRead)
def create_alert(
        alert_create: AlertCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    手动创建告警

    允许管理员手动创建自定义告警
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")

    alert = Alert(**alert_create.model_dump())
    alert.status = AlertStatus.UNHANDLED

    db.add(alert)
    db.commit()
    db.refresh(alert)

    # 记录操作日志
    record_operation(
        db,
        user_id=current_user.id,
        username=current_user.username,
        action=OperationLogger.Actions.CREATE_ALERT,
        detail=f"手动创建告警: {alert.title}",
        resource_type=OperationLogger.Resources.ALERT,
        resource_id=str(alert.id)
    )

    return AlertRead.model_validate(alert)
