from typing import Generator
from faker import Faker
from pluggy import PluginManager
import pytest
from src.chercher import hookspecs, hookimpl, Document

fake = Faker()


class DummyPlugin:
    @hookimpl
    def ingest(self, uri: str) -> Generator[Document, None, None]:
        yield Document(uri=uri, body="", metadata={})


@pytest.fixture
def plugin_manager():
    pm = PluginManager("chercher")
    pm.add_hookspecs(hookspecs)

    return pm


def test_dummy_ingest_plugin(plugin_manager):
    plugin_manager.register(DummyPlugin())
    uri = fake.file_path(depth=3)

    for documents in plugin_manager.hook.ingest(uri=uri):
        for doc in documents:
            assert doc.uri == uri
