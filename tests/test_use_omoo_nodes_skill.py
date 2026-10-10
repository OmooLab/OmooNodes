import json
import runpy
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).parents[1]
SKILL = ROOT / ".agents" / "skills" / "use-omoo-nodes"
REFERENCES = SKILL / "references"
DOCS = ROOT / "docs" / "nodes"
HELPER = SKILL / "scripts" / "omoo_blender.py"


def load_catalog() -> dict[str, object]:
    return json.loads(
        (REFERENCES / "node-catalog.json").read_text(encoding="utf-8")
    )


def test_node_catalog_contains_all_published_assets() -> None:
    catalog = load_catalog()
    assets = catalog["assets"]
    essentials = [
        asset
        for asset in assets
        if asset["source_file"].startswith("O_Essentials_")
    ]
    extra = [
        asset
        for asset in assets
        if asset["source_file"] == "O_Extra.blend"
    ]

    assert catalog["asset_count"] == 92
    assert len(assets) == 92
    assert len(essentials) == 86
    assert len(extra) == 6
    assert len({asset["name"] for asset in assets}) == 92


def test_generated_reference_has_one_section_per_asset() -> None:
    essentials = (DOCS / "o-essentials.md").read_text(encoding="utf-8")
    extra = (DOCS / "o-extra.md").read_text(encoding="utf-8")

    assert essentials.count("\n### O ") == 86
    assert extra.count("\n### O ") == 6


def test_configured_asset_roots_reject_unsynchronized_remote_cache(
    monkeypatch,
    tmp_path: Path,
) -> None:
    local_root = tmp_path / "local"
    remote_root = tmp_path / "remote"
    invalid_root = tmp_path / "invalid"
    for path in (local_root, remote_root, invalid_root):
        path.mkdir()

    libraries = [
        SimpleNamespace(
            name="Local",
            path=str(local_root),
            enabled=True,
            remote_url="",
            use_remote_url=False,
        ),
        SimpleNamespace(
            name="Remote",
            path=str(remote_root),
            enabled=True,
            remote_url="https://example.com/assets/",
            use_remote_url=True,
        ),
        SimpleNamespace(
            name="Invalid",
            path=str(invalid_root),
            enabled=True,
            remote_url="https://example.com/invalid/",
            use_remote_url=False,
        ),
    ]
    fake_bpy = SimpleNamespace(
        context=SimpleNamespace(
            preferences=SimpleNamespace(
                filepaths=SimpleNamespace(asset_libraries=libraries),
            ),
        ),
        path=SimpleNamespace(abspath=lambda value: value),
    )
    monkeypatch.setitem(sys.modules, "bpy", fake_bpy)
    helper = runpy.run_path(str(HELPER))

    assert helper["configured_asset_roots"]() == (
        local_root.resolve(),
        remote_root.resolve(),
    )


def test_remote_libraries_use_blender_remote_operator(
    monkeypatch,
    tmp_path: Path,
) -> None:
    libraries = []
    calls = []
    save_calls = []

    def add_library(**kwargs):
        calls.append(kwargs)
        cache = tmp_path / kwargs["name"].replace(" ", "_")
        cache.mkdir()
        libraries.append(
            SimpleNamespace(
                name=kwargs["name"],
                path=str(cache),
                enabled=True,
                remote_url=kwargs["remote_url"],
                use_remote_url=True,
            )
        )
        return {"FINISHED"}

    fake_bpy = SimpleNamespace(
        app=SimpleNamespace(version=(5, 2, 0)),
        context=SimpleNamespace(
            preferences=SimpleNamespace(
                experimental=SimpleNamespace(
                    use_remote_asset_libraries=True,
                ),
                system=SimpleNamespace(use_online_access=True),
                filepaths=SimpleNamespace(asset_libraries=libraries),
            ),
        ),
        path=SimpleNamespace(abspath=lambda value: value),
        ops=SimpleNamespace(
            preferences=SimpleNamespace(asset_library_add=add_library),
            wm=SimpleNamespace(save_userpref=lambda: save_calls.append(True)),
        ),
    )
    monkeypatch.setitem(sys.modules, "bpy", fake_bpy)
    helper = runpy.run_path(str(HELPER))

    configured = helper["ensure_omoo_remote_asset_libraries"]()

    assert len(configured) == 2
    assert [call["type"] for call in calls] == ["REMOTE", "REMOTE"]
    assert [call["name"] for call in calls] == ["O Essentials", "O Extra"]
    assert save_calls == [True]


def test_project_codex_config_enables_official_blender_mcp() -> None:
    config = tomllib.loads(
        (ROOT / ".codex" / "config.toml").read_text(encoding="utf-8")
    )
    blender = config["mcp_servers"]["blender"]

    assert blender["enabled"] is True
    assert blender["command"] == "uvx"
    assert "projects.blender.org/lab/blender_mcp.git@v1.0.0" in " ".join(
        blender["args"]
    )
    assert blender["env"] == {
        "BLENDER_MCP_HOST": "localhost",
        "BLENDER_MCP_PORT": "9876",
    }
