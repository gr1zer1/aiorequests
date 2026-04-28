from urllib.parse import urlparse,ParseResult


class Request:
    parsed_url: ParseResult | None
    def __init__(self,
                 method:str,
                 url:str,
                 headers: dict | None = None,
                 body: str | dict | None = None,
                 ):
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.body = body
    
    def _normalize_values(self):
        self.method = self.method.upper()
        self.parsed_url = urlparse(self.url)
        
    
    def to_bytes(self) -> bytes:
        self._normalize_values()

        path = self.parsed_url.path or "/"

        if self.parsed_url.query:
            path += f"?{self.parsed_url.query}"

        request_path = f"{self.method} {path} HTTP/1.1\r\n"
        
        request_headers = ""

        if "Host" not in self.headers.keys():

            request_headers += f"Host: {self.parsed_url.netloc}\r\n"
        
        for k, v in self.headers.items():
            request_headers += f"{k}: {v}\r\n"

        request_headers += "Connection: close\r\n"

        request_body = ""

        if self.body == None:
            pass
        elif type(self.body) == str:
            request_headers += "Content-Type: text/plain\r\n"
            request_body = self.body
            size_of_body = len(request_body.encode("utf-8"))
            request_headers += f"Content-Length: {size_of_body}\r\n"
        
        request = request_path + request_headers + "\r\n" + request_body

        return request.encode("utf-8")
        
