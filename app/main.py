from dotenv import load_dotenv

# 确保在其他逻辑前准备就绪
load_dotenv()

from app.core.logger import setup_logging  # noqa: E402

# 确保在其他逻辑前准备就绪
setup_logging()

from fastapi import FastAPI  # noqa: E402
from loguru import logger  # noqa: E402

from app.api.router import api_router  # noqa: E402
from app.core.middleware import LoggingMiddleware  # noqa: E402

logger.info("服务启动中")
app = FastAPI(title="政策解析", version="1.0.0")

app.add_middleware(LoggingMiddleware)

app.include_router(api_router)
