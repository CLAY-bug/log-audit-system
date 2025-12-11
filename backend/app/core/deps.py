from dataclasses import dataclass
from typing import Generator

from fastapi import Depends, Header, HTTPException, status

from app.core.security import decode_access_token
from app.db.session import SessionLocal


@dataclass
class CurrentUser:
    id: int | None
    username: str | None
    role: str | None


def get_db() -> Generator:
    """提供 SQLAlchemy Session，后续接口可通过 Depends 引用。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    """骨架版鉴权：仅解析伪 token，不连接数据库。"""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    return CurrentUser(
        id=payload.get("sub"),
        username=payload.get("username"),
        role=payload.get("role", "user"),
    )


def get_current_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """简单的 admin 校验，供后续接口依赖。"""
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user
