"""
AquaIntelli - GenAI Module: LangSmith Integration
Tracing and monitoring for all GenAI operations.
"""
import os
import logging
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def init_langsmith():
    """Initialize LangSmith tracing if configured."""
    if settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        logger.info("  [OK] LangSmith tracing enabled")
        print("  [OK] LangSmith tracing enabled")
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        print("  [OK] LangSmith tracing disabled (no API key)")


def get_trace_info() -> dict:
    """Get current LangSmith configuration status."""
    return {
        "tracing_enabled": os.environ.get("LANGCHAIN_TRACING_V2", "false") == "true",
        "project": settings.LANGCHAIN_PROJECT,
        "has_api_key": bool(settings.LANGCHAIN_API_KEY),
    }
