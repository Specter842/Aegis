class AegisError(Exception):
    """Base exception for AEGIS"""
    pass

class ScannerError(AegisError):
    """Raised when a scanner fails execution"""
    def __init__(self, message: str, scanner_name: str, original_error: Exception | None = None):
        super().__init__(f"Scanner {scanner_name} failed: {message}")
        self.scanner_name = scanner_name
        self.original_error = original_error

class CriticalScannerError(ScannerError):
    """Raised when a critical scanner fails, which should fail the whole pipeline"""
    pass

class PolicyError(AegisError):
    """Raised when the policy engine cannot determine a valid decision"""
    pass

class PayloadValidationError(AegisError):
    """Raised when request violates strict size/depth limits"""
    pass
