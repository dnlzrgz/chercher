from typing import Generator
from faker import Faker
import pytest
from src.chercher import hook_impl
from src.chercher.hookspecs import get_plugin_manager
from src.chercher.models import Document

fake = Faker()


class SingleIngestPlugin:
    @hook_impl
    def ingest(self, uri: str) -> Generator[Document, None, None]:
        yield Document(uri=uri, content="", metadata={})


class MultipleIngestPlugin:
    @hook_impl
    def ingest(self, uri: str) -> Generator[Document, None, None]:
        for i in range(3):
            yield Document(uri=uri, content=f"{i + 1}", metadata={})


class ErrorRaisingIngestPlugin:
    @hook_impl
    def ingest(self, uri: str) -> Generator[Document, None, None]:
        try:
            raise ValueError("An error occurred while ingesting the document.")
        except Exception as e:
            print(e)


@pytest.fixture
def plugin_manager():
    return get_plugin_manager()


def test_dummy_ingest_plugin(plugin_manager):
    plugin_manager.register(SingleIngestPlugin())
    uri = fake.file_path(depth=3)
    for document in plugin_manager.hook.ingest(uri=uri):
        assert document.uri == uri


def test_multiple_ingest_plugin(plugin_manager):
    plugin_manager.register(MultipleIngestPlugin())
    uri = fake.file_path(depth=3)

    documents = list(plugin_manager.hook.ingest(uri=uri))
    assert len(documents) > 0

    for i, doc in enumerate(documents):
        assert doc.uri == uri
        assert doc.content == f"{i + 1}"


def test_ingest_with_plugin_raising_exception(plugin_manager):
    plugin_manager.register(ErrorRaisingIngestPlugin())
    plugin_manager.register(MultipleIngestPlugin())

    uri = fake.file_path(depth=3)
    for doc in plugin_manager.hook.ingest(uri=uri):
        assert doc.uri == uri
