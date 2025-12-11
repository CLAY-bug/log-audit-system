from fastapi import APIRouter

from app.api.v1.endpoints import admin, alerts, auth, logs, ping, stats

api_router = APIRouter()

# 健康检查/环境探针
api_router.include_router(ping.router, tags=["health"])

# 以下为骨架路由，占位便于后续填充实现
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
