class AsyncHttpError(Exception):
    """Base exception"""

class ConnectError(AsyncHttpError):
    """Failed to connect to host"""

class TimeoutError(AsyncHttpError):
    """Connection or read timed out"""

class DNSError(AsyncHttpError):
    """Failed to resolve hostname"""