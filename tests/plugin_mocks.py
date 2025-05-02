from typing import Generator
from src.chercher import hookimpl, Document


class BadPlugin:
    @hookimpl
    def ingest(self, uri: str) -> Generator[Document, None, None]:
        if not uri.endswith(".txt"):
            raise Exception("Ooops!")

    @hookimpl
    def prune(self, uri: str) -> bool | None:
        if not uri.endswith(".txt"):
            raise Exception("Ooops!")


class DummyPlugin:
    @hookimpl
    def ingest(self, uri: str) -> Generator[Document, None, None]:
        yield Document(uri=uri, title=None, body="", hash=None, metadata={})

    @hookimpl
    def prune(self, uri: str) -> bool | None:
        return True


class DummyTxtPlugin:
    def __init__(
        self,
        title: str = "",
        body: str = "",
        hash: str = "",
        metadata: dict = {},
    ) -> None:
        self.title = title
        self.body = body
        self.hash = hash
        self.metadata = metadata

    @hookimpl
    def ingest(self, uri: str) -> Generator[Document, None, None]:
        if uri.endswith(".txt"):
            yield Document(
                uri=uri,
                body=self.body,
                title=self.title,
                hash=self.hash,
                metadata=self.metadata,
            )

    @hookimpl
    def prune(self, uri: str) -> bool | None:
        return uri.endswith(".txt")
