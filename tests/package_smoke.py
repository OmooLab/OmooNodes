"""Check an installed wheel or sdist without importing repository sources."""

import subprocess
import tempfile
from pathlib import Path

import omoonodes


assert not Path(omoonodes.__file__).resolve().is_relative_to(
    Path(__file__).resolve().parents[1] / "src"
), "Expected the installed package, not repository sources"

with tempfile.TemporaryDirectory() as directory:
    project = Path(directory)
    (project / "pyproject.toml").write_text('[tool.omoonodes]\ntargets = ["b45"]\n')
    source = project / "nodes/Probe"
    source.mkdir(parents=True)
    (source / "collection.json").write_text(
        '{"files": {"Probe.blend": {"source": "geometry"}}}'
    )
    (source / "geometry").mkdir()
    (source / "geometry/probe.py").write_text('''from omoonodes.builder import CustomGeometryGroup

class Probe(CustomGeometryGroup):
    _name = "Probe"

    def _build_group(self, tree):
        value = tree.inputs.float("Value", 2.0)
        result = tree.outputs.float("Result")
        value * 3.0 >> result

ASSET = Probe
''')
    subprocess.run(["omoonodes", "build", "-o", "built"], cwd=project, check=True)
    blend = project / "built/b45/Probe/Probe.blend"
    assert blend.is_file()
    subprocess.run(["omoonodes", "dump", str(blend), "-o", "exported"], cwd=project, check=True)
    code = (project / "exported/Probe/geometry/probe.py").read_text(encoding="utf8")
    assert "class Probe(" in code and '"Value"' in code and '"Result"' in code
    # Exported code must also build successfully using the installed package.
    subprocess.run(["omoonodes", "build", "exported", "-o", "rebuilt"], cwd=project, check=True)
    assert (project / "rebuilt/b45/exported/Probe.blend").is_file()
