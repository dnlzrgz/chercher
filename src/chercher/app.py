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
)
from textual.containers import Container
from textual.validation import Number
from textual.reactive import reactive
from chercher.settings import APP_NAME, APP_DIR, Settings
from chercher.db import db_connection

settings = Settings()

# TODO: add notifications.
# TODO: signal input errors.
# TODO: enter to open link.
# TODO: improve tab navigation (?).
# TODO: add theming.
# TODO: add loading indicator.


class ChercherApp(App):
    TITLE = APP_NAME
    BINDINGS = [
        ("ctrl+q", "quit", "quit"),
    ]

    CSS_PATH = "styles.tcss"

    search_query: reactive[str] = reactive("")
    n_results: reactive[int] = reactive(10)

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

        with ListView(classes="results") as results:
            results.border_title = "results"
            pass

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
    def search(self) -> None:
        if not self.search_query:
            return

        results_list = self.query_one(".results")
        results_list.clear()

        with db_connection(settings.db_url) as conn:
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

            cursor.execute(sql_query, (self.search_query, self.n_results))
            results = cursor.fetchall()
            if not results:
                self.notify("no results found")
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


if __name__ == "__main__":
    app = ChercherApp()
    app.run()
