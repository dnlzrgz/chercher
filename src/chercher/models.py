from pydantic import BaseModel


class Document(BaseModel):
    uri: str
    title: str | None = None
    body: str
    hash: str | None = None
    metadata: dict = {}
