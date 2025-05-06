import sys
import sqlite3
import click
from loguru import logger
import pluggy
from chercher.utils import console
from chercher.output import print_plugins_table, print_results_list, print_results_table
from chercher.plugin_manager import get_plugin_manager
from chercher.settings import Settings, APP_NAME, APP_DIR
from chercher.db import init_db, db_connection


logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
    level="INFO",
)
logger.add(
    APP_DIR / "chercher_errors.log",
    rotation="10 MB",
    retention="15 days",
    level="ERROR",
)

settings = Settings()


@click.group(help=settings.description)
@click.version_option(
    version=settings.version,
    message="v%(version)s",
    package_name=APP_NAME,
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    with db_connection(settings.db_url) as conn:
        logger.debug("initializing the database")
        init_db(conn)

    ctx.ensure_object(dict)
    ctx.obj["settings"] = settings
    ctx.obj["db_url"] = settings.db_url
    ctx.obj["pm"] = get_plugin_manager()


def _index(conn: sqlite3.Connection, uris: list[str], pm: pluggy.PluginManager) -> None:
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


@cli.command(help="Index documents, webpages and more.")
@click.argument("uris", nargs=-1)
@click.pass_context
def index(ctx: click.Context, uris: list[str]) -> None:
    pm = ctx.obj["pm"]
    db_url = ctx.obj["db_url"]

    if not pm.list_name_plugin():
        logger.warning("No plugins registered!")
        return

    with db_connection(db_url) as conn:
        _index(conn, uris, pm)


def _prune(conn: sqlite3.Connection, pm: pluggy.PluginManager) -> None:
    cursor = conn.cursor()
    plugin_settings = dict(settings).get("plugin", {})

    try:
        cursor.execute("SELECT uri, hash FROM documents")
        uris_and_hashes = cursor.fetchall()
    except Exception as e:
        logger.error(
            f"something went wrong while retrieving documents from the database: {e}"
        )
        return

    for uri, hash in uris_and_hashes:
        try:
            for result in pm.hook.prune(uri=uri, hash=hash, settings=plugin_settings):
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
        cursor.execute("VACUUM;")
        logger.info("vacuum completed successfully")
    except Exception as e:
        logger.error(f"something went wrong while performing vacuum operation: {e}")
        return

    logger.info("database cleanup completed")


@cli.command(help="Prune unnecessary documents from the database.")
@click.pass_context
def prune(ctx: click.Context) -> None:
    pm = ctx.obj["pm"]
    db_url = ctx.obj["db_url"]

    with db_connection(db_url) as conn:
        _prune(conn, pm)


@cli.command(help="Seach for documents matching your query.")
@click.argument("query")
@click.option(
    "-l",
    "--limit",
    type=int,
    default=5,
    help="Number of results.",
)
@click.option(
    "-o",
    "--output",
    type=click.Choice(["table", "list"], case_sensitive=False),
    default="table",
    help="Output format (available options: table and list).",
)
@click.pass_context
def search(ctx: click.Context, query: str, limit: int, output: str = "table") -> None:
    db_url = ctx.obj["db_url"]

    with db_connection(db_url) as conn:
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

        if not results:
            console.print(f"No results found for: '{query}'")
            return

        if output == "list":
            print_results_list(results)
        else:
            print_results_table(results)


@cli.command(help="List out all the registered plugins and their hooks.")
@click.pass_context
def plugins(ctx: click.Context) -> None:
    pm = ctx.obj["pm"]
    print_plugins_table(pm)
