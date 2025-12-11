from sqlalchemy.orm import declarative_base

Base = declarative_base()

# 导入 models 以便 Base.metadata 包含所有表；后续填充实际模型。
try:
    from app import models  # noqa: F401
except Exception:  # noqa: BLE001
    # 模型还未实现时忽略导入错误，保持骨架可运行。
    models = None
