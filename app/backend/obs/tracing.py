"""
Internal Observability Module — Legacy Tracing placeholder.
Now primarily used to signal if observability features are configured.
"""
def tracing_enabled() -> bool:
    # Tracing Cloud đã bị gỡ bỏ theo yêu cầu. Dashboard Local luôn được bật.
    return True

class DummyContext:
    def update_current_trace(self, **kwargs): pass
    def update_current_observation(self, **kwargs): pass
    def flush(self): pass

langfuse_context = DummyContext()

def observe(*args, **kwargs):
    def decorator(func):
        return func
    return decorator
