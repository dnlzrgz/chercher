from typing import Any
import sqlite3
from loguru import logger
import pluggy
from rich.progress import Progress
from chercher.settings import settings


def index(conn: sqlite3.Connection, uris: list[str], pm: pluggy.PluginManager) -> None:
    cursor = conn.cursor()
    plugin_settings = dict(settings).get("plugin", {})

    for uri in uris:
        try:
            for documents in pm.hook.ingest(uri=uri, settings=plugin_settings):
                for doc in documents:
                    try:
                        cursor.execute(
                            """
                    INSERT INTO documents (uri, title, body, hash, metadata) VALUES (?, ?, ?, ?, ?)
                    """,
                            (
                                doc.uri,
                                doc.title,
                                doc.body,
                                doc.hash,
                                doc.metadata.model_dump_json(),
                            ),
                        )
                        conn.commit()
                        logger.info(f'document "{doc.uri}" indexed')
                    except sqlite3.IntegrityError:
                        logger.warning(f'document "{doc.uri}" already exists')
                    except Exception as e:
                        logger.error(
                            f"something went wrong while indexing '{doc.uri}': {e}"
                        )
        except Exception as e:
            logger.error(
                f"something went wrong while trying to index documents from '{uri}': {e}"
            )


def prune(conn: sqlite3.Connection, pm: pluggy.PluginManager) -> None:
    cursor = conn.cursor()
    plugin_settings = dict(settings).get("plugin", {})
    with Progress(transient=True) as progress:
        task = progress.add_task(description="getting documents...", total=1)

        try:
            cursor.execute("SELECT uri, hash FROM documents")
            uris_and_hashes = cursor.fetchall()
        except Exception as e:
            logger.error(
                f"something went wrong while retrieving documents from the database: {e}"
            )
            return

        progress.update(task, advance=0.25, description="pruning documents...")
        for uri, hash in uris_and_hashes:
            try:
                for result in pm.hook.prune(
                    uri=uri, hash=hash, settings=plugin_settings
                ):
                    if not result:
                        continue

                    try:
                        cursor.execute("DELETE FROM documents WHERE uri = ?", (uri,))
                        conn.commit()
                        logger.info(f"document '{uri}' pruned")
                    except Exception as e:
                        logger.error(f"something went wrong while purging '{uri}': {e}")
            except Exception as e:
                logger.error(
                    f"something went wrong while trying to purge document '{uri}': {e}"
                )

        try:
            progress.update(task, advance=0.25, description="cleaning up database...")
            cursor.execute("VACUUM;")
            cursor.execute("PRAGMA optimize;")
        except Exception as e:
            logger.error(f"something went wrong while performing vacuum operation: {e}")
            return

        progress.update(task, completed=True)
    logger.info("database cleanup completed")


def search(conn: sqlite3.Connection, query: str, limit: int) -> list[Any] | None:
    cursor = conn.cursor()
    sql_query = """
            SELECT uri, title, substr(body, 0, 300)
            FROM documents
            WHERE ROWID IN (
                SELECT ROWID
                FROM documents_fts
                WHERE documents_fts MATCH ?
                ORDER BY bm25(documents_fts)
                LIMIT ?
            )
            """

    cursor.execute(sql_query, (query, limit))
    results = cursor.fetchall()
    return results
