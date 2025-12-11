from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置（第 1 周骨架版，可用 .env 覆盖）。"""

    PROJECT_NAME: str = Field("Log Audit System", description="项目名称")
    API_V1_STR: str = Field("/api/v1", description="API 根路径")
    SQLALCHEMY_DATABASE_URI: str = Field(
        "mysql+mysqlconnector://root:password@localhost:3306/log_audit",
        description="MySQL 连接串（初稿）",
    )
    JWT_SECRET: str = Field("dev-secret-change-me", description="JWT 对称密钥")
    JWT_ALGORITHM: str = Field("HS256", description="JWT 算法")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60 * 24, description="token 过期时间（分钟）")
    PASSWORD_SALT: str = Field("log-audit-salt", description="用于 PBKDF2 的盐")
    BACKEND_CORS_ORIGINS: list[str] = Field(default_factory=list, description="允许的 CORS 来源")

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
