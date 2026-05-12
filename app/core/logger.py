import json
import logging
import logging.config
from datetime import UTC, datetime

from app.core.settings import get_settings
from app.middlewares.trace_id import get_trace_id

settings = get_settings()


class AddTraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = get_trace_id()
        return super().filter(record)


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "trace_id": getattr(record, "trace_id", "unknown"),
            "message": record.getMessage(),
            "module": record.filename,
            "function": record.funcName,
            "line": record.lineno,
        }

        if hasattr(record, "extra") and record.extra:
            for key, value in record.extra.items():
                if key not in log_entry:
                    log_entry[key] = value

        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])

        return json.dumps(log_entry, ensure_ascii=False, default=str)


is_production = settings.APP_ENVIRONMENT not in ("local", "development")

logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "app.core.logger.JSONFormatter",
        },
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s [%(trace_id)s][%(asctime)s:%(msecs)03d]"
            "[%(filename)s][%(funcName)s:%(lineno)d][%(message)s]",
            "datefmt": "%d-%m-%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "formatter": "json" if is_production else "default",
        },
    },
    "loggers": {
        "app": {"handlers": ["console"], "level": settings.LOG_ENVIRONMENT},
    },
}

logging.config.dictConfig(logger_config)
logger = logging.getLogger("app")
logger.addFilter(AddTraceIdFilter())
logger.setLevel(settings.LOG_ENVIRONMENT)
