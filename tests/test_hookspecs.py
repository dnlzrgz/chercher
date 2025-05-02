from .plugin_mocks import DummyPlugin


def test_dummy_plugin_yields_document_correctly(faker, plugin_manager):
    plugin_manager.register(DummyPlugin())
    uri = faker.file_path(extension="txt")
    documents = [
        document
        for doc_gen in plugin_manager.hook.ingest(uri=uri)
        for document in doc_gen
    ]
    assert len(documents) == 1
    assert documents[0].uri == uri


def test_dummy_plugin_yields_prune_result_correctly(faker, plugin_manager):
    plugin_manager.register(DummyPlugin())
    results = [result for result in plugin_manager.hook.prune(uri=faker.file_path())]
    assert len(results) == 1
    assert results[0]
