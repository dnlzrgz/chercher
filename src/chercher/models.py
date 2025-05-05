from pydantic import BaseModel, RootModel


class DocumentMetadata(RootModel):
    root: dict = {}


class Document(BaseModel):
    uri: str
    title: str | None = None
    body: str
    hash: str | None = None
    metadata: DocumentMetadata
