import sqlite3
import click
from pluggy import PluginManager
from chercher import hookspecs
from chercher.db import init_db, with_db


def get_plugin_manager() -> PluginManager:
    pm = PluginManager("chercher")
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints("chercher")

    return pm


class Context(object):
    def __init__(self) -> None:
        init_db("./db.sqlite3")

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
        click.echo("No plugins registered!")
        return

    with with_db("./db.sqlite3") as conn:
        cursor = conn.cursor()

        for uri in uris:
            for documents in ctx.pm.hook.ingest(uri=uri):
                for doc in documents:
                    try:
                        cursor.execute(
                            """
                    INSERT INTO documents (uri, body, metadata) VALUES (?, ?, ?)
                    """,
                            (doc.uri, doc.body, "{}"),
                        )
                        click.echo(f'Document "{uri}" indexed')
                    except sqlite3.IntegrityError:
                        click.echo(f"Document with URI {uri} already exists.")
                    except Exception as e:
                        click.echo(f"An error occurred: {e}")

        conn.commit()


@cli.command()
def search() -> None:
    click.echo("Searching documents.")


@cli.command()
@click.pass_obj
def plugins(ctx: Context) -> None:
    print(ctx.pm.list_name_plugin())
