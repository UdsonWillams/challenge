import logging
import logging.config

from app.middlewares.trace_id import get_trace_id

logger = logging.getLogger(__name__)


class AddTraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = get_trace_id()
        return super().filter(record)


custom_filter = AddTraceIdFilter()
logger.addFilter(custom_filter)
logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s [%(trace_id)s][%(asctime)s:%(msecs)03d]"
            "[%(filename)s][%(funcName)s:%(lineno)d][%(message)s]",
            "datefmt": "%d-%m-%Y %H:%M:%S",
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "app": {"handlers": ["default"], "level": "DEBUG"},
    },
}
logging.config.dictConfig(logger_config)
logger.setLevel(logging.INFO)
