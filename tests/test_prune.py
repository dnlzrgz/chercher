from src.chercher.cli import _prune
from .plugin_mocks import BadPlugin, DummyTxtPlugin


def test_prune_removes_correct_document(faker, test_db, plugin_manager):
    txt_uri = faker.file_path(depth=3, extension="txt")
    pdf_uri = faker.file_path(depth=3, extension="pdf")

    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO documents (uri, title, body, hash, metadata) VALUES (?, ?, ?, ?, ?)",
        (txt_uri, "", "", "", "{}"),
    )
    cursor.execute(
        "INSERT INTO documents (uri, title, body, hash, metadata) VALUES (?, ?, ?, ?, ?)",
        (pdf_uri, "", "", "", "{}"),
    )
    test_db.commit()

    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    assert len(documents) == 2

    plugin_manager.register(DummyTxtPlugin())
    _prune(test_db, plugin_manager)

    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    assert len(documents) == 1


def test_prune_removes_correctly_all_document(faker, test_db, plugin_manager):
    cursor = test_db.cursor()
    for i in range(3):
        uri = faker.file_path(depth=i + 1, extension="txt")
        cursor.execute(
            "INSERT INTO documents (uri, title, body, hash, metadata) VALUES (?, ?, ?, ?, ?)",
            (uri, "", "", "", "{}"),
        )
        test_db.commit()

    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    assert len(documents) == 3

    plugin_manager.register(DummyTxtPlugin())
    _prune(test_db, plugin_manager)

    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    assert len(documents) == 0


def test_purge_with_exception(faker, test_db, plugin_manager):
    cursor = test_db.cursor()

    txt_uri = faker.file_path(depth=3, extension="txt")
    pdf_uri = faker.file_path(depth=3, extension="pdf")

    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO documents (uri, title, body, hash, metadata) VALUES (?, ?, ?, ?, ?)",
        (txt_uri, "", "", "", "{}"),
    )
    cursor.execute(
        "INSERT INTO documents (uri, title, body, hash, metadata) VALUES (?, ?, ?, ?, ?)",
        (pdf_uri, "", "", "", "{}"),
    )
    test_db.commit()

    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    assert len(documents) == 2

    plugin_manager.register(BadPlugin())
    plugin_manager.register(DummyTxtPlugin())
    _prune(test_db, plugin_manager)

    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    assert len(documents) == 1
