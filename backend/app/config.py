"""全局配置：从 .env 读取，未配置项使用安全默认值。"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 应用
    APP_NAME: str = "轻量AI助手"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 数据库（MySQL 8.0）
    DATABASE_URL: str = (
        "mysql+pymysql://root:296114@127.0.0.1:3306/ai_assistant?charset=utf8mb4"
    )

    # JWT 鉴权
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7

    # 登录频率限制（防暴力破解，进程内简易实现）
    LOGIN_FAIL_LIMIT: int = 5
    LOGIN_FAIL_WINDOW_SECONDS: int = 600

    # 大模型 API（OpenAI 兼容接口，经后端转发，Key 不暴露前端）
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.deepseek.com/v1"
    LLM_MODEL: str = "deepseek-chat"
    # 未配置 Key 时开启 mock 流式输出，便于前端联调；配置真实 Key 后改为 false
    MOCK_LLM: bool = True

    # 文件解析限制
    FILE_MAX_MB: int = 10
    FILE_MAX_PAGES: int = 50
    FILE_MAX_CHARS: int = 200000  # 超出后截断进入上下文的文本长度

    # AI 绘图（选型待定，预留）
    DRAW_API_KEY: str = ""
    DRAW_BASE_URL: str = ""
    DRAW_MODEL: str = ""

    # CORS（前端开发服务器地址）
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
