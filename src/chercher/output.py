import textwrap
from pluggy import PluginManager
from rich.table import Table
from chercher.utils import console


def print_results_table(results: list[dict] = []) -> None:
    table = Table(
        title="results",
        show_lines=True,
        width=80,
        padding=1,
    )
    table.add_column("title")
    table.add_column("summary")

    for result in results:
        title = f"[link={result[0]}]{result[1]}[/]"
        summary = f"{textwrap.shorten(result[2], width=280, placeholder='...')}"
        table.add_row(title, summary)

    console.print(table)


def print_results_list(results: list[dict] = []) -> None:
    grid = Table(
        title="results",
        expand=True,
        width=80,
        show_lines=False,
        show_footer=False,
        show_header=False,
        show_edge=False,
    )
    grid.add_column(justify="left")

    for result in results:
        uri = result[0]
        title = f"[link={uri}][bold]{result[1]}[/]"
        summary = f"{textwrap.shorten(result[2], width=280, placeholder='...')}\n"

        grid.add_row(f"{title}\n{uri}\n{summary}")

    console.print(grid)


def print_plugins_table(pm: PluginManager) -> None:
    table = Table(title="plugins")
    table.add_column("name")
    table.add_column("version")
    table.add_column("hooks")

    plugins = dict(pm.list_plugin_distinfo())
    for plugin, dist_info in plugins.items():
        version = f"v{dist_info.version}" if dist_info else "n/a"
        hooks = [h.name for h in pm.get_hookcallers(plugin)]
        hooks_str = ", ".join(hooks)
        table.add_row(plugin.__name__, version, hooks_str)

    console.print(table)
