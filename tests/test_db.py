import sqlite3
import pytest
from faker import Faker
from src.chercher.db import init_db

fake = Faker()


@pytest.fixture
def mock_db():
    conn = sqlite3.connect(":memory:")
    init_db(conn)

    yield conn
    conn.close()


def test_init_db(mock_db):
    cursor = mock_db.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documents';"
    )
    assert cursor.fetchone() is not None

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documents_fts';"
    )
    assert cursor.fetchone() is not None


def test_document_insertion(mock_db):
    uri = fake.file_path(depth=3)
    cursor = mock_db.cursor()
    cursor.execute(
        "INSERT INTO documents (uri, body, metadata) VALUES (?, ?, ?)",
        (uri, "", "{}"),
    )
    mock_db.commit()

    cursor.execute("SELECT * FROM documents WHERE uri = ?", (uri,))
    document = cursor.fetchone()
    assert document[0] == uri
