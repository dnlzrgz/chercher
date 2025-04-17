from typing import Generator
import pluggy
from chercher.models import Document

hookspec = pluggy.HookspecMarker("chercher")
hookimpl = pluggy.HookimplMarker("chercher")


@hookspec
def ingest(uri: str) -> Generator[Document, None, None]:
    raise NotImplementedError
