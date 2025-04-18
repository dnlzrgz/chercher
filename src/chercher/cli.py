import sys
import sqlite3
import click
from pluggy import PluginManager
from loguru import logger
from chercher import hookspecs
from chercher.db import init_db, db_connection

logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | {message}",
    level="INFO",
)
logger.add(
    "./app.log",
    rotation="10 MB",
    retention="10 days",
    level="ERROR",
)


def get_plugin_manager() -> PluginManager:
    pm = PluginManager("chercher")
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints("chercher")

    return pm


class Context(object):
    def __init__(self) -> None:
        self.db_url = "./db.sqlite3"
        with db_connection(self.db_url) as conn:
            init_db(conn)

        self.pm = get_plugin_manager()


@click.group()
@click.pass_context
def cli(ctx) -> None:
    ctx.obj = Context()


@cli.command()
@click.argument("uris", nargs=-1)
@click.pass_obj
def index(ctx: Context, uris: list[str]) -> None:
    if not ctx.pm.list_name_plugin():
        logger.warning("No plugins registered!")
        return

    with db_connection(ctx.db_url) as conn:
        cursor = conn.cursor()

        for uri in uris:
            for documents in ctx.pm.hook.ingest(uri=uri):
                for doc in documents:
                    try:
                        cursor.execute(
                            """
                    INSERT INTO documents (uri, body, metadata) VALUES (?, ?, ?)
                    """,
                            (doc.uri, doc.body, doc.metadata),
                        )
                        logger.info(f'document "{uri}" indexed')
                    except sqlite3.IntegrityError:
                        logger.warning(f'document "{uri}" already exists')
                    except Exception as e:
                        logger.error(f"an error occurred: {e}")

        conn.commit()


@cli.command()
def search() -> None:
    click.echo("Searching documents.")


@cli.command()
@click.pass_obj
def plugins(ctx: Context) -> None:
    print(ctx.pm.list_name_plugin())
