import pytest
import pluggy
from src.chercher import HOOK_NAMESPACE, Document, IngestSpec


class DummyIngestPlugin:
    @pluggy.HookimplMarker(HOOK_NAMESPACE)
    def ingest(self, uri: str) -> Document:
        return Document(
            uri=uri,
            content="Dummy content",
            details={},
        )


@pytest.fixture
def plugin_manager():
    pm = pluggy.PluginManager(HOOK_NAMESPACE)
    pm.add_hookspecs(IngestSpec)
    pm.register(DummyIngestPlugin())

    return pm


def test_ingest_plugin(plugin_manager):
    uri = "https://python.org"
    document = plugin_manager.hook.ingest(uri=uri)
    assert document.uri == uri
    assert document.content == "Dummy content"
