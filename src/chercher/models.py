from pydantic import BaseModel


class Document(BaseModel):
    uri: str
    body: str
    hash: str | None = None
    metadata: dict = {}
