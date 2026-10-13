"""Every authored Deform asset must have a node-named unit test."""

import ast
from pathlib import Path

def test_deform_catalog_has_unit_tests():
    root = Path(__file__).resolve().parents[2] / "nodes/O_Essentials"
    catalog = next(line.split(":")[0] for line in (root / "blender_assets.cats.txt").read_text().splitlines()
                   if ":O Essentials/Deform:" in line)
    assets = set()
    for path in (root / "O_Essentials_GeometryNodes/geometry").glob("*.py"):
        for item in ast.parse(path.read_text(encoding="utf8")).body:
            if isinstance(item, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ASSET_METADATA" for t in item.targets):
                if ast.literal_eval(item.value).get("catalog_id") == catalog:
                    assets.add(path.stem.removeprefix("o_"))
    covered = {path.stem.removeprefix("test_o_") for path in
               (Path(__file__).parent / "O_Essentials/geometry").glob("test_o_*.py")}
    assert assets, "Deform catalog is empty"
    assert not assets - covered, f"Missing Deform unit tests: {sorted(assets - covered)}"
