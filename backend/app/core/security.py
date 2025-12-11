import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict

from fastapi import HTTPException, status

from app.core.config import settings


def get_password_hash(password: str) -> str:
    """使用 PBKDF2-SHA256 做一个简单的哈希（后续可替换成 bcrypt/passlib）。"""
    salt = settings.PASSWORD_SALT.encode("utf-8")
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return base64.urlsafe_b64encode(dk).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """恒定时间比较，避免时序攻击。"""
    computed = get_password_hash(plain_password)
    return hmac.compare_digest(computed, hashed_password)


def _encode(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def _decode(token: str) -> Dict[str, Any]:
    try:
        raw = base64.urlsafe_b64decode(token.encode("utf-8"))
        return json.loads(raw.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def create_access_token(data: Dict[str, Any], expires_minutes: int | None = None) -> str:
    """极简“伪 JWT”实现，满足第 1 周骨架演示；后续可换 jose/pyjwt。"""
    expires_delta = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    to_encode = {**data, "exp": int(time.time()) + expires_delta * 60}
    return _encode(to_encode)


def decode_access_token(token: str) -> Dict[str, Any]:
    payload = _decode(token)
    exp = payload.get("exp")
    if exp is not None and int(exp) < int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    return payload
