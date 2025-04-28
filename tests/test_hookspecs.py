from typing import Generator
from faker import Faker
from src.chercher import hookimpl, Document

fake = Faker()

expected_doc = Document(
    uri=fake.file_path(depth=3),
    title=" ".join(fake.words()),
    body="\n".join(fake.sentences()),
    hash=fake.sha256(),
    metadata={},
)


class DummyPlugin:
    @hookimpl
    def ingest(self, uri: str) -> Generator[Document, None, None]:
        yield expected_doc


def test_dummy_plugin_yields_correct_document(plugin_manager):
    plugin_manager.register(DummyPlugin())
    for documents in plugin_manager.hook.ingest(uri=""):
        for doc in documents:
            assert doc.uri == expected_doc.uri
            assert doc.title == expected_doc.title
            assert doc.body == expected_doc.body
            assert doc.hash == expected_doc.hash
