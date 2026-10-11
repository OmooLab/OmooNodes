import pytest

from omoonodes import cli


@pytest.mark.parametrize(("arguments", "action", "destination"), [
    (["dev"], "dev", "workspaces"),
    (["dev", "--sync", "editing"], "sync", "editing"),
    (["build", "--target", "b45", "--self-contained"], "build", "dist"),
    (["dump", "input.blend", "-o", "imported"], "dump_sources", "imported"),
])
def test_commands_resolve_project_sources_and_user_paths(tmp_path, monkeypatch, arguments, action, destination):
    (tmp_path / "pyproject.toml").write_text('[tool.omoonodes]\nsource = "assets"\ntargets = ["b45"]\n')
    working = tmp_path / "nested"
    working.mkdir()
    monkeypatch.chdir(working)
    calls = []
    owner = cli.importing if action == "dump_sources" else cli.libraries
    monkeypatch.setattr(owner, action, lambda *args: calls.append(args))
    cli.main(arguments)
    source = working / "input.blend" if action == "dump_sources" else tmp_path / "assets"
    assert calls[0][:2] == (source, working / destination)
    if action == "build":
        assert calls[0][2:] == ("b45", False, True)


def test_build_defaults_to_nodes_without_tool_configuration(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'consumer'\n")
    monkeypatch.chdir(tmp_path)
    calls = []
    monkeypatch.setattr(cli.libraries, "build", lambda *args: calls.append(args))
    cli.main(["build"])
    assert calls == [(tmp_path / "nodes", tmp_path / "dist", None, False, False)]
