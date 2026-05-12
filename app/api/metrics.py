from http import HTTPStatus

from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter(tags=["Metrics"])

_REQUEST_COUNT = 0
_ERROR_COUNT = 0


def increment_request_count():
    global _REQUEST_COUNT
    _REQUEST_COUNT += 1


def increment_error_count():
    global _ERROR_COUNT
    _ERROR_COUNT += 1


@router.get("/metrics", status_code=HTTPStatus.OK)
def get_metrics() -> Response:
    metrics = (
        f"# HELP http_requests_total Total HTTP requests\n"
        f"# TYPE http_requests_total counter\n"
        f"http_requests_total {_REQUEST_COUNT}\n"
        f"# HELP http_errors_total Total HTTP errors\n"
        f"# TYPE http_errors_total counter\n"
        f"http_errors_total {_ERROR_COUNT}\n"
    )
    return Response(content=metrics, media_type="text/plain")
