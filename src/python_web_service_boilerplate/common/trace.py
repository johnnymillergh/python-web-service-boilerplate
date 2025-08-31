from __future__ import annotations

import uuid
from contextvars import ContextVar

# Context variable to store the current trace ID
_trace_id_context: ContextVar[str | None] = ContextVar("trace_id", default=None)


def generate_trace_id() -> str:
    """Generate a new unique trace ID."""
    return str(uuid.uuid4().hex)


def set_trace_id(trace_id: str) -> None:
    """Set the trace ID for the current context."""
    _trace_id_context.set(trace_id)


def get_trace_id() -> str | None:
    """Get the current trace ID from context."""
    return _trace_id_context.get()


def get_or_create_trace_id() -> str:
    """Get the current trace ID or create a new one if none exists."""
    trace_id = get_trace_id()
    if trace_id is None:
        trace_id = generate_trace_id()
        set_trace_id(trace_id)
    return trace_id


def clear_trace_id() -> None:
    """Clear the trace ID from the current context."""
    _trace_id_context.set(None)
