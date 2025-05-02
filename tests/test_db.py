def test_init_db_creates_required_tables(test_db):
    cursor = test_db.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documents';"
    )
    documents_table = cursor.fetchone()
    assert documents_table is not None
    assert documents_table[0] == "documents"

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documents_fts';"
    )
    documents_fts_table = cursor.fetchone()
    assert documents_fts_table is not None
    assert documents_fts_table[0] == "documents_fts"


def test_document_insertion_saves_correctly(faker, test_db):
    uri = faker.file_path(depth=3)
    title = " ".join(faker.words())
    body = "\n".join(faker.sentences())
    hash = faker.sha256()

    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO documents (uri, title, body, hash, metadata) VALUES (?, ?, ?, ?, ?)",
        (uri, title, body, hash, "{}"),
    )
    test_db.commit()

    cursor.execute("SELECT * FROM documents WHERE uri = ?", (uri,))
    document = cursor.fetchone()
    assert document[0] == uri
    assert document[1] == title
    assert document[2] == body
    assert document[3] == hash

    cursor.execute("SELECT * FROM documents_fts WHERE uri = ?", (uri,))
    document = cursor.fetchone()
    assert document[0] == uri
    assert document[1] == title
