from pluggy import PluginManager
from chercher import hookspecs
from chercher.settings import APP_NAME


def get_plugin_manager() -> PluginManager:
    pm = PluginManager(APP_NAME)
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints(APP_NAME)

    return pm
