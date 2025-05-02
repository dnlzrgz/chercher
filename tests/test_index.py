from src.chercher.cli import _index
from .plugin_mocks import DummyTxtPlugin, BadPlugin


def test_index_valid_txt(faker, test_db, plugin_manager):
    plugin_manager.register(DummyTxtPlugin())
    uri = faker.file_path(extension="txt")
    _index(test_db, [uri], plugin_manager)

    cursor = test_db.cursor()
    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()

    assert len(documents) == 1
    assert documents[0][0] == uri
    assert documents[0][1] is not None
    assert documents[0][2] is not None
    assert documents[0][3] is not None


def test_index_with_exception(faker, test_db, plugin_manager):
    plugin_manager.register(DummyTxtPlugin())
    plugin_manager.register(BadPlugin())
    uris = [
        faker.file_path(depth=3, extension="pdf"),
        faker.file_path(depth=3, extension="txt"),
        faker.file_path(depth=3, extension="epub"),
    ]

    _index(test_db, uris, plugin_manager)

    cursor = test_db.cursor()
    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()

    assert len(documents) == 1


def test_index_same_document_multiple_times(faker, test_db, plugin_manager):
    plugin_manager.register(DummyTxtPlugin())
    uri = faker.file_path(depth=3, extension="txt")

    _index(test_db, [uri, uri], plugin_manager)

    cursor = test_db.cursor()
    cursor.execute("SELECT * FROM documents WHERE uri = ?", (uri,))
    documents = cursor.fetchall()

    assert len(documents) == 1
    assert documents[0][0] == uri
