import sqlite3
import pytest
from faker import Faker
from pluggy import PluginManager
from src.chercher.db import init_db
from src.chercher import hookspecs

fake = Faker()


@pytest.fixture
def plugin_manager():
    pm = PluginManager("chercher")
    pm.add_hookspecs(hookspecs)

    return pm


@pytest.fixture
def test_db():
    conn = sqlite3.connect(":memory:")
    init_db(conn)

    yield conn
    conn.close()
