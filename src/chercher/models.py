from pydantic import BaseModel


class Document(BaseModel):
    uri: str
    body: str
    metadata: dict = {}
