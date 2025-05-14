import sys
from loguru import logger
import click
from chercher.utils import console
from chercher.output import print_plugins_table, print_results_list, print_results_table
from chercher.plugin_manager import get_plugin_manager
from chercher.settings import settings, APP_NAME, APP_DIR, CONFIG_FILE_PATH
from chercher.app import ChercherApp
from chercher.db import init_db, db_connection
from chercher.db_actions import index, prune, search

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


@cli.command(
    name="index",
    help="Index documents, webpages and more.",
)
@click.argument("uris", nargs=-1)
@click.pass_context
def index_cmd(ctx: click.Context, uris: list[str]) -> None:
    pm = ctx.obj["pm"]
    db_url = ctx.obj["db_url"]

    if not pm.list_name_plugin():
        logger.warning("No plugins registered!")
        return

    with db_connection(db_url) as conn:
        index(conn, uris, pm)


@cli.command(
    name="prune",
    help="Prune unnecessary documents from the database.",
)
@click.pass_context
def prune_cmd(ctx: click.Context) -> None:
    pm = ctx.obj["pm"]
    db_url = ctx.obj["db_url"]

    with db_connection(db_url) as conn:
        prune(conn, pm)


@cli.command(
    name="search",
    help="Seach for documents matching your query.",
)
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
def search_cmd(
    ctx: click.Context, query: str, limit: int, output: str = "table"
) -> None:
    db_url = ctx.obj["db_url"]

    with db_connection(db_url) as conn:
        results = search(conn, query, limit)
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


@cli.command(
    help="Print the location of the configuration file or the database.",
)
@click.argument(
    "item",
    type=click.Choice(["config", "db"]),
)
def locate(item: str) -> None:
    if item == "config":
        console.print(
            f"config file located at: [url={CONFIG_FILE_PATH.absolute()}]{CONFIG_FILE_PATH.absolute()}[/]"
        )
    elif item == "db":
        console.print(f"db located at: [url={settings.db_url}]{settings.db_url}[/]")


@cli.command(
    help="Starts the TUI.",
)
def app() -> None:
    app = ChercherApp()
    app.run()


if __name__ == "__main__":
    cli()
