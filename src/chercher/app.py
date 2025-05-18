from datetime import datetime, timedelta
from importlib.metadata import version
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import (
    Footer,
    Label,
    Input,
    Button,
    Link,
    ListItem,
    ListView,
    Tree,
)
from textual.containers import Container
from textual.validation import Number
from textual.reactive import reactive
from chercher.settings import APP_NAME, APP_DIR, Settings
from chercher.db import db_connection
from chercher.db_actions import search, load_history

settings = Settings()

# TODO: add notifications.
# TODO: signal input errors.
# TODO: enter to open link.
# TODO: improve tab navigation (?).
# TODO: add loading indicator.


def format_date(date_str: str) -> str:
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    today = datetime.today().date()
    yesterday = today - timedelta(days=1)

    if date == today:
        return "today"
    elif date == yesterday:
        return "yesterday"
    else:
        return date_str


class ChercherApp(App):
    TITLE = APP_NAME
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        ("ctrl+q", "quit", "quit"),
    ]

    CSS_PATH = "styles.tcss"

    search_query: reactive[str] = reactive("")
    n_results: reactive[int] = reactive(10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme = settings.theme

    def on_mount(self):
        self.load_history()

    def compose(self) -> ComposeResult:
        with Container(classes="header"):
            yield Label(f"↪ {APP_NAME}", classes="title")
            yield Label(f"v{version(APP_NAME)}", classes="version")
            yield Label(f"{APP_DIR}", classes="path")

        with Container(classes="search-bar"):
            yield Input(
                placeholder="search...",
                type="text",
                classes="input input--query",
            )
            yield Input(
                placeholder="10",
                type="integer",
                validators=Number(minimum=1, maximum=100),
                classes="input input--n-results",
            )
            yield Button(label="search", classes="submit")

        with Container(classes="main") as _:
            with Tree(classes="history", label="*") as history:
                history.show_root = False
                history.show_guides = True
                history.root.expand()

                history.border_title = "history"

            with ListView(classes="results") as results:
                results.border_title = "results"

        yield Footer()

    @on(Input.Changed, selector=".input--query")
    def update_search_query(self, event: Input.Changed) -> None:
        self.search_query = event.value

    @on(Input.Changed, selector=".input--n-results")
    def update_number_of_results(self, event: Input.Changed) -> None:
        try:
            self.n_results = int(event.value)
        except Exception:
            self.n_results = 1

    @on(Input.Submitted)
    @on(Button.Pressed)
    def submit(self) -> None:
        if not self.search_query:
            return

        results_list: ListView = self.query_one(".results")
        results_list.clear()
        results_list.loading = True

        with db_connection(settings.db_url) as conn:
            results = search(conn, self.search_query, self.n_results)
            if not results:
                self.notify(f'no results found for "{self.search_query}"')
                results_list.loading = False
                return

            for result in results:
                results_list.mount(
                    ListItem(
                        Link(
                            result[1] or result[0],
                            url=result[0],
                            tooltip="click to open",
                        ),
                        classes="result",
                    ),
                )

        self.load_history()
        results_list.loading = False

    @on(Tree.NodeSelected)
    def search_from_history(self, event: Tree.NodeSelected) -> None:
        if event.node.data and event.node.data.get("is_root", False):
            return

        search_input: Input = self.query_one(".input--query")
        self.search_query = f"{event.node.label}"
        search_input.value = self.search_query
        search_input.focus(True)

    def load_history(self) -> None:
        history_tree: Tree = self.query_one(".history")
        history_tree.clear()
        history_tree.loading = True

        with db_connection(settings.db_url) as conn:
            entries = load_history(conn)
            if not entries:
                history_tree.loading = False
                return

            for date, queries in entries:
                date_str = format_date(date)
                today_or_yesterday = date_str in ("today", "yesterday")
                date_root = history_tree.root.add(
                    f"{format_date(date)}",
                    expand=today_or_yesterday,
                    data={"is_root": True},
                )
                for query in queries.split(","):
                    date_root.add_leaf(query)

            history_tree.loading = False


if __name__ == "__main__":
    app = ChercherApp()
    app.run()
