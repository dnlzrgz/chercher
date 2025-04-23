from faker import Faker

fake = Faker()


def test_init_db(test_db):
    cursor = test_db.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documents';"
    )
    assert cursor.fetchone() is not None

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documents_fts';"
    )
    assert cursor.fetchone() is not None


def test_document_insertion(test_db):
    uri = fake.file_path(depth=3)
    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO documents (uri, body, metadata) VALUES (?, ?, ?)",
        (uri, "", "{}"),
    )
    test_db.commit()

    cursor.execute("SELECT * FROM documents WHERE uri = ?", (uri,))
    document = cursor.fetchone()
    assert document[0] == uri

    cursor.execute("SELECT * FROM documents_fts WHERE uri = ?", (uri,))
    document = cursor.fetchone()
    assert document[0] == uri
