"""
Logging Configuration and Utilities
Provides structured logging throughout the application
"""

import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from app.config import settings

# Reserved LogRecord attribute names that cannot be used in extra dict
RESERVED_LOG_RECORD_ATTRS = {
    'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname',
    'levelno', 'lineno', 'module', 'msecs', 'message', 'pathname', 'process',
    'processName', 'relativeCreated', 'thread', 'threadName', 'exc_info',
    'exc_text', 'stack_info', 'taskName'
}


def _filter_reserved_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """Filter out reserved LogRecord attribute names from log data"""
    return {k: v for k, v in data.items() if k not in RESERVED_LOG_RECORD_ATTRS}


def setup_logging():
    """Configure application-wide logging"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module"""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    user_id: Optional[str] = None,
    **kwargs
):
    """Log HTTP request"""
    log_data = {
        "method": method,
        "path": path,
        "user_id": user_id,
        **kwargs
    }
    # Filter out reserved LogRecord attributes to avoid conflicts
    filtered_data = _filter_reserved_keys(log_data)
    logger.info(f"Request: {method} {path}", extra=filtered_data)


def log_response(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: Optional[float] = None,
    user_id: Optional[str] = None,
    **kwargs
):
    """Log HTTP response"""
    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "user_id": user_id,
        **kwargs
    }
    # Filter out reserved LogRecord attributes to avoid conflicts
    filtered_data = _filter_reserved_keys(log_data)
    level = logging.ERROR if status_code >= 400 else logging.INFO
    logger.log(level, f"Response: {method} {path} - {status_code}", extra=filtered_data)


def log_evaluation_event(
    logger: logging.Logger,
    event_type: str,
    evaluation_id: str,
    user_id: Optional[str] = None,
    **kwargs
):
    """Log evaluation-related events"""
    log_data = {
        "event_type": event_type,
        "evaluation_id": evaluation_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    }
    # Filter out reserved LogRecord attributes to avoid conflicts
    filtered_data = _filter_reserved_keys(log_data)
    logger.info(f"Evaluation Event: {event_type} - {evaluation_id}", extra=filtered_data)


def log_agent_event(
    logger: logging.Logger,
    agent_type: str,
    evaluation_id: str,
    event: str,
    **kwargs
):
    """Log agent-related events"""
    log_data = {
        "agent_type": agent_type,
        "evaluation_id": evaluation_id,
        "event": event,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    }
    # Filter out reserved LogRecord attributes to avoid conflicts
    filtered_data = _filter_reserved_keys(log_data)
    logger.info(f"Agent Event: {agent_type} - {event} - {evaluation_id}", extra=filtered_data)


def log_websocket_event(
    logger: logging.Logger,
    event_type: str,
    evaluation_id: str,
    user_id: Optional[str] = None,
    **kwargs
):
    """Log WebSocket-related events"""
    log_data = {
        "event_type": event_type,
        "evaluation_id": evaluation_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    }
    # Filter out reserved LogRecord attributes to avoid conflicts
    filtered_data = _filter_reserved_keys(log_data)
    logger.info(f"WebSocket Event: {event_type} - {evaluation_id}", extra=filtered_data)


def log_document_event(
    logger: logging.Logger,
    event_type: str,
    document_id: str,
    user_id: Optional[str] = None,
    **kwargs
):
    """Log document-related events"""
    log_data = {
        "event_type": event_type,
        "document_id": document_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    }
    # Filter out reserved LogRecord attributes to avoid conflicts
    filtered_data = _filter_reserved_keys(log_data)
    logger.info(f"Document Event: {event_type} - {document_id}", extra=filtered_data)


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Optional[str] = None,
    **kwargs
):
    """Log errors with context"""
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    }
    # Filter out reserved LogRecord attributes to avoid conflicts
    filtered_data = _filter_reserved_keys(log_data)
    logger.error(
        f"Error: {type(error).__name__}: {str(error)}" + (f" - Context: {context}" if context else ""),
        exc_info=True,
        extra=filtered_data
    )

