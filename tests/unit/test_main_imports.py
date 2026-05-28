import main as main_module


def test_main_module_imports_build_graph():
    assert hasattr(main_module, "build_graph")
    assert callable(main_module.build_graph)
