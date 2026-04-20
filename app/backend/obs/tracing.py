"""
Tích hợp Langfuse distributed tracing cho TA_Chatbot (Tương thích v3.x).
Dùng OpenTelemetry-based architecture của Langfuse v3.
"""
from __future__ import annotations
import os
from typing import Any

try:
    # --- Langfuse v3 Syntax ---
    from langfuse import observe, get_client
    _LANGFUSE_AVAILABLE = True
    _IMPORT_ERROR = None

    # Tạo một lớp giả lập langfuse_context để tương thích với code cũ (v2)
    class LangfuseContextProxy:
        def update_current_trace(self, **kwargs: Any) -> None:
            try:
                get_client().update_current_trace(**kwargs)
            except: pass
        
        def update_current_observation(self, **kwargs: Any) -> None:
            try:
                get_client().update_current_span(**kwargs)
            except: pass
            
        def flush(self) -> None:
            try:
                get_client().flush()
            except: pass

    langfuse_context = LangfuseContextProxy()

except Exception as e:
    # --- Fallback khi không có thư viện ---
    _LANGFUSE_AVAILABLE = False
    _IMPORT_ERROR = str(e)

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None: return None
        def update_current_observation(self, **kwargs: Any) -> None: return None
        def flush(self) -> None: return None

    langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    """Kiểm tra xem Langfuse tracing đã được cấu hình chưa."""
    pk = os.getenv("LANGFUSE_PUBLIC_KEY")
    sk = os.getenv("LANGFUSE_SECRET_KEY")
    
    if not _LANGFUSE_AVAILABLE:
        # Chỉ in log nếu thực sự thiếu thư viện, không in nếu chỉ là sai syntax import
        print(f"❌ LANGFUSE SDK ERROR: {_IMPORT_ERROR}")
        
    return bool(_LANGFUSE_AVAILABLE and pk and sk)
