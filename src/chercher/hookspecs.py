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
    def ingest(self, uri: str) -> Document | list[Document] | None:
        pass
