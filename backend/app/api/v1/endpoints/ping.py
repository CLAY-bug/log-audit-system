from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", summary="测试接口：验证服务可用")
def ping():
    return {"message": "pong"}
