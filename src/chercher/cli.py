import sys
import sqlite3
import textwrap
import click
from loguru import logger
import pluggy
from rich.console import Console
from rich.table import Table
from chercher.plugin_manager import get_plugin_manager
from chercher.settings import Settings, APP_NAME, APP_DIR
from chercher.db import init_db, db_connection

console = Console()

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

    for uri in uris:
        try:
            for documents in pm.hook.ingest(uri=uri, settings=dict(settings)):
                for doc in documents:
                    try:
                        cursor.execute(
                            """
                    INSERT INTO documents (uri, body, hash, metadata) VALUES (?, ?, ?, ?)
                    """,
                            (doc.uri, doc.body, doc.hash, "{}"),
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


@cli.command(help="Seach for documents matching your query.")
@click.argument("query")
@click.option(
    "-l",
    "--limit",
    type=int,
    default=5,
    help="Number of results.",
)
@click.pass_context
def search(ctx: click.Context, query: str, limit: int) -> None:
    db_url = ctx.obj["db_url"]

    with db_connection(db_url) as conn:
        cursor = conn.cursor()

        sql_query = """
            SELECT uri, substr(body, 0, 300)
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

        for result in results:
            console.print(f"[link={result[0]}]{result[0]}[/]")
            console.print(
                f"{textwrap.shorten(result[1], width=280, placeholder='...')}\n",
                highlight=False,
            )


@cli.command(help="List out all the registered plugins and their hooks.")
@click.pass_context
def plugins(ctx: click.Context) -> None:
    pm = ctx.obj["pm"]
    plugins = dict(pm.list_plugin_distinfo())

    table = Table(title="plugins")
    table.add_column("name")
    table.add_column("hooks")

    for plugin in plugins:
        hooks = [h.name for h in pm.get_hookcallers(plugin)]
        hooks_str = ", ".join(hooks)
        table.add_row(plugin.__name__, hooks_str)

    console.print(table)
