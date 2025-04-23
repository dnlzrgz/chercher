import sqlite3
import pytest
from pluggy import PluginManager
from src.chercher.db import init_db
from src.chercher import hookspecs


@pytest.fixture
def plugin_manager():
    pm = PluginManager("chercher")
    pm.add_hookspecs(hookspecs)

    return pm


@pytest.fixture
def test_db(tmp_path):
    db_path = tmp_path / "chercher_test.db"
    conn = sqlite3.connect(db_path)
    init_db(conn)

    yield conn
    conn.close()
