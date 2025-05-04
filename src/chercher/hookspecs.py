from typing import Generator
import pluggy
from chercher.models import Document

hookspec = pluggy.HookspecMarker("chercher")
hookimpl = pluggy.HookimplMarker("chercher")


@hookspec
def ingest(uri: str, settings: dict) -> Generator[Document, None, None]:
    pass


@hookspec
def prune(uri: str, settings: dict) -> bool | None:
    pass
