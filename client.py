from session import Session

class Client:
    def __init__(self,headers: dict[str,str] | None = None):
        self.headers = headers
        self.session: Session = Session(self)

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.session.close_all_conn()
