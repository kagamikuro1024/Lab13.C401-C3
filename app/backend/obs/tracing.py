"""
Tích hợp Langfuse distributed tracing cho TA_Chatbot.
Nếu không có LANGFUSE keys trong .env, fallback về dummy (không crash).
"""
from __future__ import annotations

import os
from typing import Any

try:
    from langfuse.decorators import langfuse_context, observe  # type: ignore
    _LANGFUSE_AVAILABLE = True
except Exception:
    # Langfuse chưa cài hoặc chưa cấu hình — dùng dummy để không crash
    _LANGFUSE_AVAILABLE = False

    def observe(*args: Any, **kwargs: Any):  # type: ignore
        """Decorator giả lập khi Langfuse không khả dụng."""
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

        def flush(self) -> None:
            return None

    langfuse_context = _DummyContext()  # type: ignore


def tracing_enabled() -> bool:
    """Kiểm tra xem Langfuse tracing đã được cấu hình chưa."""
    return bool(
        _LANGFUSE_AVAILABLE
        and os.getenv("LANGFUSE_PUBLIC_KEY")
        and os.getenv("LANGFUSE_SECRET_KEY")
    )
