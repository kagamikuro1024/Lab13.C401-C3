"""
Langfuse Tracing Integration for TA_Chatbot.
Tác giả: Trung (Day 13 Observability Lab)
"""
from __future__ import annotations

import os
from functools import wraps
from typing import Any, Callable, Optional

try:
    from langfuse.decorators import observe as langfuse_observe
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("⚠️  Warning: langfuse not installed. Tracing disabled.")


# === Initialize Langfuse Client ===
def _init_langfuse() -> Optional[Langfuse]:
    """Khởi tạo Langfuse client từ environment variables."""
    if not LANGFUSE_AVAILABLE:
        return None
    
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    if not (public_key and secret_key):
        return None
    
    try:
        client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )
        return client
    except Exception as e:
        print(f"⚠️  Failed to init Langfuse: {e}")
        return None


# Global Langfuse instance
_langfuse_client = _init_langfuse()


def tracing_enabled() -> bool:
    """Kiểm tra xem Langfuse tracing có bật không."""
    return LANGFUSE_AVAILABLE and _langfuse_client is not None


class LangfuseContext:
    """Wrapper context cho Langfuse traces — API tương thích với codebase hiện tại."""
    
    def __init__(self):
        self.current_trace = None
        self.current_observation = None
    
    def update_current_trace(self, **kwargs) -> None:
        """Update metadata của trace hiện tại."""
        if not _langfuse_client or not self.current_trace:
            return
        
        if "tags" in kwargs:
            self.current_trace.tags = kwargs["tags"]
        if "metadata" in kwargs:
            self.current_trace.update(metadata=kwargs["metadata"])
    
    def update_current_observation(self, **kwargs) -> None:
        """Update metadata của observation hiện tại."""
        if not _langfuse_client or not self.current_observation:
            return
        
        if "tags" in kwargs:
            self.current_observation.tags = kwargs["tags"]
        if "metadata" in kwargs:
            self.current_observation.update(metadata=kwargs["metadata"])
    
    def flush(self) -> None:
        """Flush pending traces to Langfuse."""
        if _langfuse_client:
            _langfuse_client.flush()


langfuse_context = LangfuseContext()


def observe(name: Optional[str] = None, **decorator_kwargs) -> Callable:
    """
    Decorator để tracing function với Langfuse.
    Nếu Langfuse chưa available, decorator vẫn hoạt động bình thường (pass-through).
    
    Usage:
        @observe(name="my_function")
        def my_function(arg1, arg2):
            ...
    """
    def actual_decorator(func: Callable) -> Callable:
        # Nếu không có Langfuse, return function gốc
        if not tracing_enabled():
            return func
        
        # Dùng Langfuse decorator
        func_name = name or func.__name__
        langfuse_decorator = langfuse_observe(name=func_name, **decorator_kwargs)
        return langfuse_decorator(func)
    
    # Hỗ trợ cả @observe hay @observe(name="...")
    if callable(name):
        # Case: @observe (không có parentheses)
        func = name
        name = None
        return actual_decorator(func)
    else:
        # Case: @observe(name="...") (có parentheses)
        return actual_decorator
