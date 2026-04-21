import sys
from typing import Any
from app.core.config import settings
from app.core.exceptions import PayloadValidationError

def enforce_payload_limits(payload_bytes: int, prompt_length: int, history_items: int, max_message_length: int):
    """
    Enforce global constraints on incoming requests to prevent DoS attacks.
    """
    if payload_bytes > settings.MAX_PAYLOAD_BYTES:
        raise PayloadValidationError(f"Payload too large. Max allowed is {settings.MAX_PAYLOAD_BYTES} bytes.")
    
    if prompt_length > settings.MAX_PROMPT_CHARS:
        raise PayloadValidationError(f"Prompt is too long. Max allowed is {settings.MAX_PROMPT_CHARS} characters.")
        
    if history_items > settings.MAX_HISTORY_ITEMS:
        raise PayloadValidationError(f"Too many history items. Max allowed is {settings.MAX_HISTORY_ITEMS}.")
        
    if max_message_length > settings.MAX_MESSAGE_CHARS:
        raise PayloadValidationError(f"A history message is too long. Max length is {settings.MAX_MESSAGE_CHARS}.")

def redact_text(text: str, max_len: int = 200, mask_middle: bool = False) -> str:
    """
    Utility to safely truncate or redact text for persistence or logging.
    """
    if not text:
        return text
        
    if len(text) <= max_len:
        if mask_middle:
            return "***[REDACTED]***"
        return text
        
    if mask_middle:
        keep = max_len // 2 - 2
        return f"{text[:keep]}...{text[-keep:]}"
        
    return f"{text[:max_len]}..."

def get_payload_size(data: Any) -> int:
    """Approximate size metric of payload object."""
    return sys.getsizeof(str(data))
