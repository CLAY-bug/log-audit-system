"""
统计分析 API Endpoints
负责人: 于凯程

提供各类统计数据接口，用于Dashboard展示
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.log import Log
from app.models.alert import Alert, AlertStatus, AlertLevel

router = APIRouter()


@router.get("/logs-by-time")
def get_logs_by_time(
        start_time: Optional[datetime] = Query(None, description="开始时间"),
        end_time: Optional[datetime] = Query(None, description="结束时间"),
        interval: str = Query("hour", description="时间间隔(hour/day)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    按时间统计日志数量

    返回指定时间范围内，按小时或按天统计的日志数量趋势

    Args:
        start_time: 开始时间，默认为24小时前
        end_time: 结束时间，默认为当前时间
        interval: 时间粒度，hour(小时)或day(天)

    Returns:
        {
            "data": [
                {"time": "2025-12-09 10:00:00", "count": 150},
                {"time": "2025-12-09 11:00:00", "count": 200},
                ...
            ],
            "total": 5000
        }
    """
    # 设置默认时间范围
    if not end_time:
        end_time = datetime.now()
    if not start_time:
        start_time = end_time - timedelta(hours=24)

    # 根据interval选择时间格式
    if interval == "hour":
        time_format = "%Y-%m-%d %H:00:00"
    else:  # day
        time_format = "%Y-%m-%d"

    # 查询统计数据
    results = db.query(
        func.date_format(Log.timestamp, time_format).label('time_slot'),
        func.count(Log.id).label('count')
    ).filter(
        and_(
            Log.timestamp >= start_time,
            Log.timestamp <= end_time
        )
    ).group_by('time_slot').order_by('time_slot').all()

    # 统计总数
    total = db.query(func.count(Log.id)).filter(
        and_(
            Log.timestamp >= start_time,
            Log.timestamp <= end_time
        )
    ).scalar()

    # 格式化结果
    data = [
        {"time": result.time_slot, "count": result.count}
        for result in results
    ]

    return {
        "data": data,
        "total": total,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "interval": interval
    }


@router.get("/logs-by-level")
def get_logs_by_level(
        start_time: Optional[datetime] = Query(None, description="开始时间"),
        end_time: Optional[datetime] = Query(None, description="结束时间"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    按日志级别统计

    返回各级别(INFO/WARN/ERROR等)的日志数量

    Returns:
        {
            "data": [
                {"level": "INFO", "count": 3000},
                {"level": "WARN", "count": 500},
                {"level": "ERROR", "count": 100}
            ],
            "total": 3600
        }
    """
    # 构建查询
    query = db.query(
        Log.level,
        func.count(Log.id).label('count')
    )

    # 应用时间筛选
    if start_time:
        query = query.filter(Log.timestamp >= start_time)
    if end_time:
        query = query.filter(Log.timestamp <= end_time)

    # 分组统计
    results = query.group_by(Log.level).all()

    # 统计总数
    total_query = db.query(func.count(Log.id))
    if start_time:
        total_query = total_query.filter(Log.timestamp >= start_time)
    if end_time:
        total_query = total_query.filter(Log.timestamp <= end_time)
    total = total_query.scalar()

    # 格式化结果
    data = [
        {
            "level": result.level or "UNKNOWN",
            "count": result.count,
            "percentage": round(result.count / total * 100, 2) if total > 0 else 0
        }
        for result in results
    ]

    return {
        "data": data,
        "total": total
    }


@router.get("/logs-by-source")
def get_logs_by_source(
        start_time: Optional[datetime] = Query(None, description="开始时间"),
        end_time: Optional[datetime] = Query(None, description="结束时间"),
        top_n: int = Query(10, ge=1, le=50, description="返回前N个来源"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    按日志来源统计

    返回各来源系统的日志数量

    Returns:
        {
            "data": [
                {"source": "web_app", "count": 2000},
                {"source": "database", "count": 800},
                ...
            ],
            "total": 5000
        }
    """
    query = db.query(
        Log.source,
        func.count(Log.id).label('count')
    )

    if start_time:
        query = query.filter(Log.timestamp >= start_time)
    if end_time:
        query = query.filter(Log.timestamp <= end_time)

    results = query.group_by(Log.source).order_by(
        func.count(Log.id).desc()
    ).limit(top_n).all()

    # 统计总数
    total_query = db.query(func.count(Log.id))
    if start_time:
        total_query = total_query.filter(Log.timestamp >= start_time)
    if end_time:
        total_query = total_query.filter(Log.timestamp <= end_time)
    total = total_query.scalar()

    data = [
        {
            "source": result.source or "UNKNOWN",
            "count": result.count,
            "percentage": round(result.count / total * 100, 2) if total > 0 else 0
        }
        for result in results
    ]

    return {
        "data": data,
        "total": total
    }


@router.get("/top-ips")
def get_top_ips(
        start_time: Optional[datetime] = Query(None, description="开始时间"),
        end_time: Optional[datetime] = Query(None, description="结束时间"),
        top_n: int = Query(10, ge=1, le=50, description="返回前N个IP"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    统计访问最频繁的IP地址

    用于识别活跃或可疑的IP
    """
    query = db.query(
        Log.ip,
        func.count(Log.id).label('count')
    ).filter(Log.ip.isnot(None))

    if start_time:
        query = query.filter(Log.timestamp >= start_time)
    if end_time:
        query = query.filter(Log.timestamp <= end_time)

    results = query.group_by(Log.ip).order_by(
        func.count(Log.id).desc()
    ).limit(top_n).all()

    data = [
        {"ip": result.ip, "count": result.count}
        for result in results
    ]

    return {"data": data}


@router.get("/alerts-trend")
def get_alerts_trend(
        start_time: Optional[datetime] = Query(None, description="开始时间"),
        end_time: Optional[datetime] = Query(None, description="结束时间"),
        interval: str = Query("day", description="时间间隔(hour/day)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    告警趋势统计

    按时间统计告警产生数量
    """
    if not end_time:
        end_time = datetime.now()
    if not start_time:
        start_time = end_time - timedelta(days=7)

    if interval == "hour":
        time_format = "%Y-%m-%d %H:00:00"
    else:
        time_format = "%Y-%m-%d"

    results = db.query(
        func.date_format(Alert.created_at, time_format).label('time_slot'),
        func.count(Alert.id).label('count')
    ).filter(
        and_(
            Alert.created_at >= start_time,
            Alert.created_at <= end_time
        )
    ).group_by('time_slot').order_by('time_slot').all()

    data = [
        {"time": result.time_slot, "count": result.count}
        for result in results
    ]

    return {"data": data}


@router.get("/dashboard-summary")
def get_dashboard_summary(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Dashboard汇总数据

    返回Dashboard页面需要的各类统计数据
    """
    # 计算时间范围
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    # 日志统计
    total_logs = db.query(func.count(Log.id)).scalar()
    today_logs = db.query(func.count(Log.id)).filter(
        Log.timestamp >= today_start
    ).scalar()

    # 告警统计
    total_alerts = db.query(func.count(Alert.id)).scalar()
    unhandled_alerts = db.query(func.count(Alert.id)).filter(
        Alert.status == AlertStatus.UNHANDLED
    ).scalar()
    critical_alerts = db.query(func.count(Alert.id)).filter(
        and_(
            Alert.alert_level == AlertLevel.CRITICAL,
            Alert.status.in_([AlertStatus.UNHANDLED, AlertStatus.HANDLING])
        )
    ).scalar()

    # 最近7天的日志趋势
    recent_logs = db.query(
        func.date_format(Log.timestamp, "%Y-%m-%d").label('date'),
        func.count(Log.id).label('count')
    ).filter(
        Log.timestamp >= week_ago
    ).group_by('date').order_by('date').all()

    # 按级别统计最近的日志
    logs_by_level = db.query(
        Log.level,
        func.count(Log.id).label('count')
    ).filter(
        Log.timestamp >= today_start
    ).group_by(Log.level).all()

    return {
        "logs": {
            "total": total_logs,
            "today": today_logs,
            "recent_trend": [
                {"date": r.date, "count": r.count}
                for r in recent_logs
            ],
            "by_level": {
                r.level: r.count for r in logs_by_level
            }
        },
        "alerts": {
            "total": total_alerts,
            "unhandled": unhandled_alerts,
            "critical": critical_alerts
        },
        "timestamp": now.isoformat()
    }
