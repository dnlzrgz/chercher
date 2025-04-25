from typing import Generator
from faker import Faker
from src.chercher.cli import _index
from src.chercher import hookimpl, Document

fake = Faker()


class BadPlugin:
    @hookimpl
    def ingest(self, uri: str) -> Generator[Document, None, None]:
        if not uri.endswith(".txt"):
            raise Exception("Ooops!")


class DummyTxtPlugin:
    @hookimpl
    def ingest(self, uri: str) -> Generator[Document, None, None]:
        if uri.endswith(".txt"):
            yield Document(
                uri=uri,
                body=fake.sentence(),
                metadata={},
            )


def test_index_valid_txt(test_db, plugin_manager):
    plugin_manager.register(DummyTxtPlugin())
    uri = fake.file_path(depth=3, extension="txt")
    _index(test_db, [uri], plugin_manager)

    cursor = test_db.cursor()
    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    assert len(documents) == 1
    assert documents[0][0] == uri


def test_index_with_exception(test_db, plugin_manager):
    plugin_manager.register(DummyTxtPlugin())
    plugin_manager.register(BadPlugin())
    uris = [
        fake.file_path(depth=3, extension="pdf"),
        fake.file_path(depth=3, extension="txt"),
        fake.file_path(depth=3, extension="epub"),
    ]

    _index(test_db, uris, plugin_manager)

    cursor = test_db.cursor()
    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()

    assert len(documents) == 1


def test_index_same_document_multiple_times(test_db, plugin_manager):
    plugin_manager.register(DummyTxtPlugin())
    uri = fake.file_path(depth=3, extension="txt")

    _index(test_db, [uri, uri], plugin_manager)

    cursor = test_db.cursor()
    cursor.execute("SELECT * FROM documents WHERE uri = ?", (uri,))
    documents = cursor.fetchall()

    assert len(documents) == 1
    assert documents[0][0] == uri
