from pydantic import BaseModel


class Document(BaseModel):
    uri: str
    content: str
    metadata: dict = {}
