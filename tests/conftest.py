"""Options shared by repository test entry points."""


def pytest_addoption(parser):
    parser.addoption("--node-target", help="Run node behavior cases for one configured Blender target")
