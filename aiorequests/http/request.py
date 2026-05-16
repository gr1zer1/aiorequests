import json
from urllib.parse import urlparse, ParseResult
from aiorequests.errors.exception import PortError


class Request:
    parsed_url: ParseResult | None

    def __init__(self, method: str, url: str, headers: dict | None = None, body: dict | str | None = None):
        self.method = method.upper()
        self.url = url
        self.headers = headers or {}
        self.body = body

        self._fix_url()

        self.parsed_url = urlparse(self.url)
    
    def _fix_url(self):
        if "://" not in self.url:
            self.url = "http://" + self.url
    
    

    def to_bytes(self) -> bytes:
        
        path = self.parsed_url.path or "/"
        if self.parsed_url.query:
            path += f"?{self.parsed_url.query}"

        request_path = f"{self.method} {path} HTTP/1.1\r\n"

        headers = dict(self.headers)

        if "Host" not in headers:
            headers["Host"] = self.parsed_url.hostname


        body_bytes = b""

        if self.body is not None:
            if isinstance(self.body, str):
                body_bytes = self.body.encode("utf-8")
                headers["Content-Type"] = "text/plain; charset=utf-8"

            elif isinstance(self.body, dict):
                body_bytes = json.dumps(self.body).encode("utf-8")
                headers["Content-Type"] = "application/json"

            headers["Content-Length"] = str(len(body_bytes))

        request_headers = ""
        for k, v in headers.items():
            request_headers += f"{k}: {v}\r\n"

        request = request_path + request_headers + "\r\n"

        return request.encode("utf-8") + body_bytes


    @property
    def port(self) -> int:
        if self.parsed_url.port is not None:
            return self.parsed_url.port
        elif self.parsed_url.scheme == "http":
            return 80
        elif self.parsed_url.scheme == "https":
            return 443
        
        else:
            raise PortError
