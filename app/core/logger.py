import logging
import sys
from typing import cast
from types import FrameType

from loguru import logger
from app.core.config import settings

class InterceptHandler(logging.Handler):
    """
    默认使用的 python logging handler 会拦截并把日志转发给 loguru。
    详情可以参考：https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """
    def emit(self, record: logging.LogRecord) -> None:
        # 尝试获取对应记录的日志等级
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # 定位被 logger 接管掉的调用方所在的 frame 位置
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging() -> None:
    """初始化并配置系统级日志，接管原生 logging 输出"""
    
    # 1. 移除 loguru 已有的默认 Handler，避免重复输出
    logger.remove()
    
    # 2. 依据配置决定控制台格式是否是 json
    serialize_console = settings.LOG_FORMAT.lower() == "json"

    # 添加控制台(标准输出)日志，作为开发调试或某些基础收集平台使用
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        serialize=serialize_console,
        enqueue=True, # 异步处理保证线程安全
        backtrace=True,
        diagnose=True,
    )
    
    # 3. 添加文件日志，并开启 json 序列化以实现“符合工业标准”结构化存储并支持轮转
    # 对于文件日志，生产环境中通常强制使用 json 并将文件滚动以便于 Filebeat/Logstash 等收集
    logger.add(
        settings.LOG_FILE_PATH,
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        serialize=True, # 文件始终为 JSON 格式满足工业标准需求
        enqueue=True,
        backtrace=True,
        diagnose=False, # 生产文件尽量关掉过度详细的 locals 解析（取决于需要，由于日志量可能大这里关闭diagnose增加安全性）
    )

    # 4. 接管 Uvicorn 和 FastAPI 等原生日志引擎
    logging.getLogger().handlers = [InterceptHandler()]
    
    for logger_name in (
        "uvicorn.asgi",
        "uvicorn.access",
        "uvicorn",
        "fastapi",
    ):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler(level=settings.LOG_LEVEL)]
        logging_logger.propagate = False
        
    logger.info("系统日志服务已启动并接管原生 Loggings (配置：级别={}, Console={}, File={})", 
                settings.LOG_LEVEL, 
                "JSON" if serialize_console else "Text", 
                settings.LOG_FILE_PATH)
