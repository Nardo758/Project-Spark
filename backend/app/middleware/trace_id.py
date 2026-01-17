"""Request trace ID middleware for log correlation."""

import uuid
import logging
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")
_old_factory = None

def get_trace_id() -> str:
    """Get the current request's trace ID."""
    return trace_id_var.get()

class TraceIdMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns a unique trace ID to each request."""
    
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())[:12]
        trace_id_var.set(trace_id)
        
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response

def install_trace_id_factory():
    """Install a LogRecord factory that adds trace_id to all log records.
    
    This is non-invasive - it preserves existing handlers and formatters.
    Formatters can use %(trace_id)s if desired.
    """
    global _old_factory
    if _old_factory is not None:
        return
    
    _old_factory = logging.getLogRecordFactory()
    
    def trace_record_factory(*args, **kwargs):
        record = _old_factory(*args, **kwargs)
        record.trace_id = get_trace_id() or "-"
        return record
    
    logging.setLogRecordFactory(trace_record_factory)

def configure_app_logging():
    """Configure app loggers to use trace_id in output format.
    
    Adds a handler with trace_id format to the 'app' logger.
    Uses propagate=False to avoid duplicate logs from root.
    """
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [trace:%(trace_id)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    
    app_logger = logging.getLogger("app")
    app_logger.addHandler(handler)
    app_logger.setLevel(logging.INFO)
    app_logger.propagate = False
