from enum import Enum

class Decision(str, Enum):
    ALLOW = "allow"
    SANITIZE = "sanitize"
    CHALLENGE = "challenge"
    BLOCK = "block"

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SourceType(str, Enum):
    USER = "user"
    SYSTEM = "system"
    TOOL = "tool"
    DOC = "document"
    DOCUMENT_CHUNK = "document_chunk"
    URL_CONTENT = "url_content"
    OUTPUT_CONTENT = "output_content"

class OutputAction(str, Enum):
    ALLOW = "allow"
    REDACT = "redact"
    TRUNCATE = "truncate"
    BLOCK = "block"

class TrustLevel(int, Enum):
    UNTRUSTED = 0
    MIXED = 1
    TRUSTED = 2

class ScanStage(str, Enum):
    PRE_PROCESS = "pre_process"
    STATIC = "static"
    ML = "ml"
    POST_PROCESS = "post_process"
