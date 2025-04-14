from typing import Generator
from collections import namedtuple
import pluggy

HOOK_NAMESPACE = "chercher"

hook_spec = pluggy.HookspecMarker(HOOK_NAMESPACE)
hook_impl = pluggy.HookimplMarker(HOOK_NAMESPACE)

Document = namedtuple("Document", ["uri", "content", "details"])


class IngestSpec:
    """
    Namespace that defines the specification for the data ingest.
    """

    @hook_spec(firstresult=True)
    def ingest(self, uri: str) -> Generator[Document, None, None]:
        raise NotImplementedError


def get_plugin_manager() -> pluggy.PluginManager:
    pm = pluggy.PluginManager(HOOK_NAMESPACE)
    pm.add_hookspecs(IngestSpec)
    pm.load_setuptools_entrypoints(HOOK_NAMESPACE)

    return pm
