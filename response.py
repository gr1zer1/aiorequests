import json
from typing import Any

class Response:
    schema: None | str    

    def __init__(self,schema: str, status_code: int, status: str, headers: dict[str,str], body:Any):
        self.schema = schema
        self.status_code = status_code
        self.status = status
        self.headers = headers
        self.body = body

    
    @staticmethod
    def _parse_status(line:str) -> tuple[str,int,str]:
        line = line.split(" ")
        return line[0],int(line[1]),f"{line[1]}_{line[2]}"
    
    @staticmethod
    def _parse_headers(headers:list[str]) -> dict[str,str]:
        parsed_headers:dict[str,str] = {}

        for header in headers:
            kv = header.split(":",1)
            parsed_headers[kv[0]] = kv[1]

        return parsed_headers


    @classmethod
    def from_bytes(cls,data: bytes):
        response_body = data.decode()

        head, body = response_body.split("\r\n\r\n", 1)
        headers = head.split("\r\n")

        schema,status_code,status = cls._parse_status(headers[0])

        headers = cls._parse_headers(headers[1:])

        parsed_body = json.loads(body)

        return cls(schema,status_code,status,headers,parsed_body)

