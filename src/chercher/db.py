import sqlite3
from contextlib import contextmanager


def init_db(sqlite_url: str) -> None:
    conn = sqlite3.connect(sqlite_url)
    cursor = conn.cursor()

    # Create the documents table.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        uri TEXT PRIMARY KEY,
        body TEXT NOT NULL,
        metadata TEXT
    );
    """)

    # Create virtual FTS5 table based on the documents table.
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5 (
        uri,
        body,
        content=documents,
        tokenize="porter unicode61 remove_diacritics 1"
    );
    """)

    # Create trigger to keep the FTS5 index up to date.
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
        INSERT INTO documents_fts(rowid, uri, body) VALUES (new.rowid, new.uri, new.body);
    END;
    """)

    # Settings
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("PRAGMA busy_timeout = 5000;")
    cursor.execute("PRAGMA temp_store = FILE;")
    cursor.execute("PRAGMA cache_size = 2000;")
    cursor.execute("PRAGMA auto_vacuum = FULL;")

    conn.commit()
    conn.close()


@contextmanager
def with_db(sqlite_url: str):
    conn = sqlite3.connect(sqlite_url)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
