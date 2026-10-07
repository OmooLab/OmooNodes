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
GENERATOR = ROOT / "scripts" / "generate_node_reference.py"
INSPECTOR = ROOT / "scripts" / "inspect_omoo_nodes.py"
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


def test_every_asset_has_a_behavior_note() -> None:
    catalog = load_catalog()
    generator = runpy.run_path(str(GENERATOR))
    notes = generator["BEHAVIOR_NOTES"]

    assert {
        asset["name"]
        for asset in catalog["assets"]
    } == set(notes)
    assert {
        asset["name"]: asset["description"]
        for asset in catalog["assets"]
    } == notes


def test_generated_reference_has_one_section_per_asset() -> None:
    essentials = (DOCS / "o-essentials.md").read_text(encoding="utf-8")
    extra = (DOCS / "o-extra.md").read_text(encoding="utf-8")

    assert essentials.count("\n### O ") == 86
    assert extra.count("\n### O ") == 6


def test_generated_reference_is_written_as_a_user_manual() -> None:
    catalog = load_catalog()
    generator = runpy.run_path(str(GENERATOR))
    asset_section = generator["asset_section"]

    for asset in catalog["assets"]:
        section = asset_section(asset)
        directions = {socket["in_out"] for socket in asset["interface"]}

        assert asset["description"] in section
        assert ("#### 输入" in section) == ("INPUT" in directions)
        assert ("#### 输出" in section) == ("OUTPUT" in directions)
        assert "| 方向 |" not in section
        assert "默认值" not in section
        assert "范围与说明" not in section
        assert "NodeSocket" not in section
        assert "源文件：" not in section
        assert "依赖：" not in section
        assert "控制节点中的" not in section
        assert "输出节点计算得到的" not in section


def test_high_value_nodes_include_practical_guidance() -> None:
    essentials = (DOCS / "o-essentials.md").read_text(encoding="utf-8")
    extra = (DOCS / "o-extra.md").read_text(encoding="utf-8")

    assert "把 `O Noise Texture` 接到 `Height`" in essentials
    assert "等于此值的位置不移动" in essentials
    assert "推动噪声随时间连续变化" in essentials
    assert "制作定格动画、手绘抖线或机械部件的轻微振动" in extra


def test_skill_covers_assets_and_readable_node_authoring() -> None:
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert "## 范围" in skill
    assert "## 使用 Omoo Nodes" in skill
    assert "## 构建节点" in skill
    assert "## 保持可读" in skill
    assert "## 验收" in skill
    assert "https://assets.omoolab.xyz/b52/O_Essentials" in skill
    assert "https://assets.omoolab.xyz/b52/O_Extra" in skill
    assert "动态任务只实现动态本身" in skill
    assert "不要创建或调整相机、灯光、背景" in skill
    assert "创建多个 Group Input" in skill
    assert "socket.hide = not socket.is_linked" in skill
    assert "不要修改其 `name` 或设置 `node.label`" in skill
    assert "Frame 和 String 说明不是默认要求" in skill
    assert "内容必须非空" in skill
    assert "不要让任何节点、Reroute、Frame 或说明节点互相重叠" in skill
    assert "自定义 Attribute 使用 `o_` 前缀" in skill
    assert "node_group.is_modifier = True" in skill
    assert "稳定 ID" in skill
    assert "Capture Attribute" in skill
    assert "坐标空间" in skill
    assert len(skill.splitlines()) <= 100


def test_generated_node_markdown_is_not_duplicated_inside_skill() -> None:
    assert not (REFERENCES / "o-essentials.md").exists()
    assert not (REFERENCES / "o-extra.md").exists()


def test_runtime_helper_stays_with_skill_and_generators_live_at_root() -> None:
    assert HELPER.is_file()
    assert GENERATOR.is_file()
    assert INSPECTOR.is_file()
    assert not (ROOT / "scripts" / "omoo_blender.py").exists()


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
