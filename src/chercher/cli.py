import sys
import sqlite3
import textwrap
import click
from loguru import logger
from rich import print as pprint
from chercher.plugin_manager import get_plugin_manager
from chercher.settings import Settings, APP_DIR
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


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    with db_connection(settings.db_url) as conn:
        logger.info("initializing the database")
        init_db(conn)

    ctx.ensure_object(dict)
    ctx.obj["settings"] = settings
    ctx.obj["db_url"] = settings.db_url
    ctx.obj["pm"] = get_plugin_manager()


@cli.command()
@click.argument("uris", nargs=-1)
@click.pass_context
def index(ctx: click.Context, uris: list[str]) -> None:
    pm = ctx.obj["pm"]
    db_url = ctx.obj["db_url"]

    if not pm.list_name_plugin():
        logger.warning("No plugins registered!")
        return

    with db_connection(db_url) as conn:
        cursor = conn.cursor()

        for uri in uris:
            for documents in pm.hook.ingest(uri=uri, settings=dict(settings)):
                for doc in documents:
                    try:
                        cursor.execute(
                            """
                    INSERT INTO documents (uri, body, metadata) VALUES (?, ?, ?)
                    """,
                            (doc.uri, doc.body, "{}"),
                        )
                        conn.commit()
                        logger.info(f'document "{uri}" indexed')
                    except sqlite3.IntegrityError:
                        logger.warning(f'document "{uri}" already exists')
                    except Exception as e:
                        logger.error(f"an error occurred: {e}")


@cli.command()
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

        for result in results:
            pprint(f"[link={result[0]}]{result[0]}[/]")
            print(f"{textwrap.shorten(result[1], width=280, placeholder='...')}\n")


@cli.command()
@click.pass_context
def plugins(ctx: click.Context) -> None:
    pm = ctx.obj["pm"]
    print(pm.list_name_plugin())
