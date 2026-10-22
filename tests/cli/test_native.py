"""Small real-Blender regressions for data that is easy to lose."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from omoonodes import importing, libraries
from omoonodes.files import write_json
from omoonodes.runtimes import configuration, run_worker, runtime_environment
from omoonodes.sources import source_files


@pytest.fixture(scope="module")
def config():
    return configuration()


def native(config, directory, code, version):
    script = directory / "edit.py"
    script.write_text(code, encoding="utf8")
    env = runtime_environment()
    for suffix in ("RESOURCES", "CONFIG", "SCRIPTS", "EXTENSIONS", "DATAFILES"):
        path = directory / "user" / suffix.lower()
        path.mkdir(parents=True, exist_ok=True)
        env["BLENDER_USER_" + suffix] = str(path)
    result = subprocess.run([config[version], str(script)], env=env, capture_output=True, text=True, encoding="utf8")
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("version", ["b45", "b52"])
def test_menu_dependency_rebuild_preserves_selections_and_rejects_stale_export(config, tmp_path, monkeypatch, version):
    root = tmp_path / "nodes"
    owner = root / "Owner"
    script = owner / "geometry/menu.py"
    script.parent.mkdir(parents=True)
    definition = '''from omoonodes import geometry as g
from omoonodes.builder import CustomGeometryGroup
class Menu(CustomGeometryGroup):
    _name = 'Menu'
    def _build_group(self, tree):
        mode = tree.inputs.menu('Mode', 'A')
        result = tree.outputs.float('Result')
        switch = tree.tree.nodes.new('GeometryNodeMenuSwitch')
        switch.data_type = 'FLOAT'
        switch.enum_items.clear()
        for name in ['A', 'B', 'C']:
            switch.enum_items.new(name)
        for name, value in [('A', 1), ('B', 2), ('C', 3)]:
            switch.inputs[name].default_value = value
        tree.tree.links.new(mode.socket, switch.inputs['Menu'])
        tree.tree.links.new(switch.outputs[0], result.socket)
ASSET = Menu
'''
    script.write_text(definition)
    write_json(owner / "collection.json", {"files": {"Owner.blend": {"source": "geometry"}}})
    extra = root / "Extra"
    consumer = extra / "geometry/consumer.py"
    consumer.parent.mkdir(parents=True)
    consumer.write_text('''from nodes.Owner.geometry.menu import Menu
from omoonodes import geometry as g
from omoonodes.builder import CustomGeometryGroup
class Consumer(CustomGeometryGroup):
    _name = 'Consumer'
    def _build_group(self, tree):
        geometry = tree.inputs.geometry('Geometry')
        result = tree.outputs.geometry('Geometry')
        offset = g.CombineXYZ(x=Menu(Mode='A'), y=Menu(Mode='B'))
        g.SetPosition(geometry=geometry, offset=offset) >> result
ASSET = Consumer
''')
    write_json(extra / "collection.json", {"dependencies": ["Owner"], "files": {
        "Extra.blend": {"source": "geometry", "links": {"Menu": {"library": "Owner", "file": "Owner.blend"}}}}})
    selected = {**config, "versions": {version: config["targets"][version]}}
    monkeypatch.setattr(libraries, "configuration", lambda *args, **kwargs: selected)
    workspace = tmp_path / "workspace"
    libraries.dev(root, workspace, version)
    old_owner = workspace / version / "Owner/Owner.blend"
    old_consumer = workspace / version / "Extra/Extra.blend"
    before = old_owner.read_bytes(), old_consumer.read_bytes()
    # Rebuilding the same labels with native IDs shifts 2/3/4 to 0/1/2.
    script.write_text(definition.replace("        switch.enum_items.clear()\n        for name in ['A', 'B', 'C']:\n            switch.enum_items.new(name)\n",
                                        "        switch.enum_items[0].name = 'A'\n        switch.enum_items[1].name = 'B'\n        switch.enum_items.new('C')\n"))
    with pytest.raises(ValueError, match="Extra depends on Owner"):
        libraries.dev(owner, workspace, version)
    assert (old_owner.read_bytes(), old_consumer.read_bytes()) == before

    # Simulate an external dependency replacement to exercise dump/inspect validation.
    candidate = tmp_path / "candidate"
    libraries.build_staged(selected, [owner], candidate, tmp_path / "build")
    shutil.copy2(candidate / version / "Owner/Owner.blend", old_owner)
    native(config, tmp_path, f'''
import bpy
bpy.ops.wm.open_mainfile(filepath={str(old_consumer)!r}, load_ui=False)
nodes = [node for node in bpy.data.node_groups['Consumer'].nodes if node.bl_idname == 'GeometryNodeGroup']
assert [node.inputs['Mode'].default_value for node in nodes] == ['C', '']
''', version)
    for action in ["inspect", "dump"]:
        with pytest.raises(subprocess.CalledProcessError) as failure:
            run_worker(config, tmp_path, action, version=version, input=str(old_consumer), output=str(tmp_path / "dump"))
        assert "Invalid menu selection: Consumer/" in failure.value.stdout
    assert not (tmp_path / "dump").exists()
    with pytest.raises(subprocess.CalledProcessError) as failure:
        run_worker(config, tmp_path, "publish", version=version, input=str(old_consumer.parent),
                   output=str(tmp_path / "published"), self_contained=True)
    assert "Invalid menu selection: Consumer/" in failure.value.stdout
    assert not (tmp_path / "published/Extra.blend").exists()

    libraries.dev(root, workspace, version)
    native(config, tmp_path, f'''
import sys
sys.path.insert(0, {str(Path(__file__).resolve().parents[1] / 'nodes')!r})
import bpy
from evaluation import geometry_group, coordinates
bpy.ops.wm.open_mainfile(filepath={str(old_consumer)!r}, load_ui=False)
nodes = [node for node in bpy.data.node_groups['Consumer'].nodes if node.bl_idname == 'GeometryNodeGroup']
assert [node.inputs['Mode'].default_value for node in nodes] == ['A', 'B']
obj, _, _ = geometry_group('Consumer', [(0, 0, 0)])
assert coordinates(obj) == [(1, 2, 0)]
''', version)


@pytest.mark.parametrize("version", ["b45", "b52"])
def test_arrangement_removes_frames_and_keeps_routes_unparented(config, tmp_path, version):
    native(config, tmp_path, f'''
import sys
sys.path.insert(0, {str(Path(__file__).resolve().parents[2] / 'src')!r})
''' + '''
import bpy
from unittest.mock import patch
from omoonodes.arrangement.arrange import arrange_nodes

for kind in ['GeometryNodeTree', 'ShaderNodeTree', 'CompositorNodeTree']:
    tree = bpy.data.node_groups.new('Old frames ' + kind, kind)
    nodes = [tree.nodes.new('ShaderNodeMath') for _ in range(5)]
    tree.links.new(nodes[0].outputs[0], nodes[-1].inputs[0])
    frame = tree.nodes.new('NodeFrame')
    frame['arrangement_frame'] = True
    nested = tree.nodes.new('NodeFrame')
    nested.parent = frame
    for node in nodes:
        node.parent = nested
    positions = {i: (i * 200, 100) for i in range(5)}
    blocks = [{'members': list(range(5))}]
    routes = {0: [(100, 100), (300, 50), (700, 400), (800, 100)]}
    with patch('omoonodes.arrangement.arrange.calculation_blocks', return_value=(blocks, set())), patch(
        'omoonodes.arrangement.arrange.plan_layout', return_value=(positions, routes)
    ):
        arrange_nodes(tree)
    assert not any(node.bl_idname == 'NodeFrame' for node in tree.nodes), kind
    assert all(node.parent is None for node in tree.nodes), kind
    assert [tuple(node.location) for node in nodes] == [(i * 200, -100) for i in range(5)]
    assert [tuple(node.location) for node in tree.nodes if node.bl_idname == 'NodeReroute'] == [(292, -42), (692, -392)]
    assert nodes[-1].inputs[0].links[0].from_node.bl_idname == 'NodeReroute'
''', version)


@pytest.mark.parametrize("version", ["b45", "b52"])
def test_arrangement_local_inputs_preserve_asset_links_on_reload(config, tmp_path, version):
    native(config, tmp_path, f'''
import sys
sys.path[:0] = [{str(Path(__file__).resolve().parents[2])!r}, {str(Path(__file__).resolve().parents[2] / 'src')!r}]
''' + '''
import bpy
from omoonodes.arrangement.arrange import arrange_nodes
from omoonodes.arrangement.common import origin_socket, socket_links
from nodes.O_Essentials.O_Essentials_CompositingNodes.compositor.o_stroke import OStroke
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_tube import OTube

shader = bpy.data.node_groups.new('Shader input reads', 'ShaderNodeTree')
shader.interface.new_socket('Value', in_out='INPUT', socket_type='NodeSocketFloat')
shader.interface.new_socket('Shader', in_out='OUTPUT', socket_type='NodeSocketShader')
inp = shader.nodes.new('NodeGroupInput')
add = shader.nodes.new('ShaderNodeAddShader')
for socket in add.inputs:
    bsdf = shader.nodes.new('ShaderNodeBsdfPrincipled')
    shader.links.new(inp.outputs['Value'], bsdf.inputs['Roughness'])
    shader.links.new(bsdf.outputs[0], socket)
shader.links.new(add.outputs[0], shader.nodes.new('NodeGroupOutput').inputs[0])

def links(tree):
    result = []
    for edge in tree.links:
        if edge.to_node.bl_idname == 'NodeReroute':
            continue
        source = origin_socket(edge.from_socket)
        name = 'Input' if source.node.bl_idname == 'NodeGroupInput' else source.node.name
        result.append((name, source.identifier, edge.to_node.name, edge.to_socket.identifier))
    return sorted(result)

trees = [OStroke.create_group(), OTube.create_group(), shader]
expected = {tree.name: links(tree) for tree in trees}
for tree in trees:
    arrange_nodes(tree)
    assert not any(node.bl_idname == 'NodeFrame' for node in tree.nodes), tree.name
    reads = [node for node in tree.nodes if node.bl_idname == 'NodeGroupInput']
    assert len(reads) > 1, tree.name
    assert all(any(socket.is_linked for socket in node.outputs) for node in reads)
    assert links(tree) == expected[tree.name], tree.name
    positions = {node.name: tuple(node.location_absolute) for node in tree.nodes if node.bl_idname not in {'NodeFrame', 'NodeReroute'}}
    arrange_nodes(tree)
    assert links(tree) == expected[tree.name], tree.name
    assert positions == {node.name: tuple(node.location_absolute) for node in tree.nodes if node.bl_idname not in {'NodeFrame', 'NodeReroute'}}, tree.name

# Distinct interface reads can intentionally repeat the same geometry input.
repeated = bpy.data.node_groups.new('Repeated interface geometry', 'GeometryNodeTree')
repeated.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
repeated.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
join = repeated.nodes.new('GeometryNodeJoinGeometry')
for index in range(3):
    read = repeated.nodes.new('NodeGroupInput')
    repeated.links.new(read.outputs[0], join.inputs[0])
    if index == 1:
        cube = repeated.nodes.new('GeometryNodeMeshCube')
        repeated.links.new(cube.outputs[0], join.inputs[0])
repeated.links.new(join.outputs[0], repeated.nodes.new('NodeGroupOutput').inputs[0])
def input_order():
    return [origin_socket(edge.from_socket).node.bl_idname for edge in socket_links(join.inputs[0])]
order = input_order()
before = links(repeated)
for _ in range(2):
    arrange_nodes(repeated)
    assert links(repeated) == before
    assert input_order() == order
from omoonodes.arrangement.source import clear_layout
clear_layout(repeated)
assert links(repeated) == before
assert input_order() == order
trees.append(repeated)
expected[repeated.name] = before

for kind in ['GeometryNodeTree', 'ShaderNodeTree', 'CompositorNodeTree']:
    tree = bpy.data.node_groups.new(kind + ' local reads', kind)
    tree.interface.new_socket('Value', in_out='INPUT', socket_type='NodeSocketFloat')
    tree.interface.new_socket('Result', in_out='OUTPUT', socket_type='NodeSocketFloat')
    read = tree.nodes.new('NodeGroupInput')
    math = [tree.nodes.new('ShaderNodeMath') for _ in range(5)]
    for node in math[:2]:
        for socket in node.inputs:
            tree.links.new(read.outputs[0], socket)
    for source, socket in zip(math[:2], math[2].inputs):
        tree.links.new(source.outputs[0], socket)
    for socket in math[3].inputs:
        tree.links.new(math[2].outputs[0], socket)
    tree.links.new(math[3].outputs[0], math[4].inputs[0])
    tree.links.new(read.outputs[0], math[4].inputs[1])
    tree.links.new(math[4].outputs[0], tree.nodes.new('NodeGroupOutput').inputs[0])
    expected[tree.name] = links(tree)
    arrange_nodes(tree)
    assert math[0].inputs[0].links[0].from_node == math[1].inputs[0].links[0].from_node, kind
    assert math[0].inputs[0].links[0].from_node != math[4].inputs[1].links[0].from_node, kind
    assert links(tree) == expected[tree.name], kind
    trees.append(tree)

''' + f'''
path = {str(tmp_path / 'arranged.blend')!r}
bpy.data.libraries.write(path, set(trees), fake_user=True, compress=True)
bpy.ops.wm.open_mainfile(filepath=path)
for name, edges in expected.items():
    tree = bpy.data.node_groups[name]
    assert not any(node.bl_idname == 'NodeFrame' for node in tree.nodes), name
    assert links(tree) == edges, name
    if name != 'Repeated interface geometry':
        assert sum(node.bl_idname == 'NodeGroupInput' for node in tree.nodes) > 1, name
''', version)


@pytest.mark.parametrize("version", ["b45", "b52"])
def test_native_roundtrips_preserve_dynamic_nodes_and_resources(config, tmp_path, version):
    blend = tmp_path / "original.blend"
    native(config, tmp_path, f'''
import sys
sys.path.insert(0, {str(Path(__file__).resolve().parents[2] / 'src')!r})
import bpy
from omoonodes.native import validate_menus
bpy.ops.wm.read_factory_settings(use_empty=True)
g=bpy.data.node_groups.new('Probe','GeometryNodeTree');g.is_modifier=True;g.asset_mark()
g.asset_data.author='Tester';g.asset_data.tags.new('test')
p=g.interface.new_panel('Settings');g.interface.new_socket('Value',in_out='INPUT',socket_type='NodeSocketFloat',parent=p)
g.interface.new_socket('Color',in_out='OUTPUT',socket_type='NodeSocketColor')
m=g.nodes.new('ShaderNodeMix');m.data_type='RGBA';next(s for s in m.inputs if s.identifier=='A_Color').default_value=(0.3,0.4,0.5,0.2)
out=g.nodes.new('NodeGroupOutput');g.links.new(next(s for s in m.outputs if s.identifier=='Result_Color'),out.inputs['Color'])
g.interface.new_socket('Mode',in_out='INPUT',socket_type='NodeSocketMenu')
menu=g.nodes.new('GeometryNodeMenuSwitch');menu.data_type='BOOLEAN'
menu.enum_items[0].name='First';menu.enum_items[1].name='Second'
g.links.new(g.nodes.new('NodeGroupInput').outputs['Mode'],menu.inputs['Menu'])
g.interface_update(bpy.context)
try:
    validate_menus(g)
except ValueError as error:
    assert 'Probe/interface/Mode' in str(error)
else:
    raise AssertionError('An unset interface menu was accepted')
g.interface.items_tree['Mode'].default_value='Second'
r=g.nodes.new('FunctionNodeRandomValue');r.data_type='FLOAT'
math=g.nodes.new('ShaderNodeMath');math.operation='MULTIPLY'
g.links.new(next(s for s in r.outputs if s.type=='VALUE' and not s.is_unavailable),math.inputs[0])
for kind, prop, old, port, new in [
    ('GeometryNodeRemoveAttribute', 'pattern_mode', 'WILDCARD', 'Pattern Mode', 'Wildcard'),
    ('GeometryNodeResampleCurve', 'mode', 'LENGTH', 'Mode', 'Length'),
    ('GeometryNodeMergeByDistance', 'mode', 'CONNECTED', 'Mode', 'Connected'),
    ('GeometryNodeSetCurveNormal', 'mode', 'FREE', 'Mode', 'Free'),
    ('GeometryNodeDistributePointsInVolume', 'mode', 'DENSITY_GRID', 'Mode', 'Grid'),
    ('GeometryNodeVolumeToMesh', 'resolution_mode', 'VOXEL_SIZE', 'Resolution Mode', 'Size'),
]:
    node=g.nodes.new(kind)
    if hasattr(node, prop):
        setattr(node, prop, old)
    else:
        node.inputs[port].default_value=new
z=g.nodes.new('GeometryNodeRepeatOutput');z.repeat_items.new('FLOAT','Value')
i=g.nodes.new('GeometryNodeRepeatInput');i.pair_with_output(z)
f=g.nodes.new('NodeFrame');f.label='Keep me';m.parent=f;m.location=(40,-50)
g.nodes.new('ShaderNodeFloatCurve').mapping.curves[0].points.new(0.3,0.7)
r=g.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements.new(0.4).color=(0.2,0.4,0.6,0.5)
a=g.nodes.new('GeometryNodeMeshCube');b=g.nodes.new('GeometryNodeMeshIcoSphere');j=g.nodes.new('GeometryNodeJoinGeometry')
g.links.new(a.outputs['Mesh'],j.inputs['Geometry']);g.links.new(b.outputs['Mesh'],j.inputs['Geometry'])
child=bpy.data.node_groups.new('Child UV','GeometryNodeTree');child.nodes.new('ShaderNodeValue').outputs[0].default_value=3
g.nodes.new('GeometryNodeGroup').node_tree=child
mat=bpy.data.materials.new('Material');mat.use_nodes=True
mat.use_backface_culling=True
mat.node_tree.nodes.new('ShaderNodeNormalMap').space='OBJECT'
mat['yp']={{'active_ypaint_node': '', 'expand_content': 0}}
image=bpy.data.images.new('Pixel',width=1,height=1);image.pixels[:]=(0.2,0.3,0.4,1);image.pack()
mat.node_tree.nodes.new('ShaderNodeTexImage').image=image
g.nodes.new('GeometryNodeSetMaterial').inputs['Material'].default_value=mat
c=bpy.data.node_groups.new('Displace','CompositorNodeTree');c.asset_mark()
d=c.nodes.new('CompositorNodeDisplace');v=c.nodes.new('ShaderNodeCombineXYZ')
c.links.new(v.outputs[0],d.inputs['Vector' if bpy.app.version < (5,0,0) else 'Displacement'])
bpy.data.libraries.write({str(blend)!r},{{g,c}},fake_user=True,compress=True)
''', version)
    previous = None
    for cycle in range(2):
        source = tmp_path / f"source-{cycle}"
        exported = run_worker(config, tmp_path, "dump", version=version, input=str(blend), output=str(source))
        files = source_files(source)
        assert 'class ChildUV(' in (source / 'geometry/_shared/child_uv.py').read_text()
        material_source = (source / 'materials/material.py').read_text()
        assert '_name = "Material"' in material_source
        assert 'MATERIAL_PROPERTIES = {\n    "use_backface_culling": True,\n}' in material_source
        assert '$custom' not in material_source
        if previous is not None:
            assert files == previous
        previous = files
        blend = tmp_path / f"cycle-{cycle}.blend"
        built = run_worker(config, tmp_path, "build", version=version, input=str(source), output=str(blend))
        assert exported['graphs'] == built['graphs']
        native(config, tmp_path, f'''
import bpy
bpy.ops.wm.open_mainfile(filepath={str(blend)!r})
menu = next(n for n in bpy.data.node_groups['Probe'].nodes if n.bl_idname == 'GeometryNodeMenuSwitch')
assert [s.identifier for s in menu.inputs if s.identifier.startswith('Item_')] == ['Item_0', 'Item_1']
assert bpy.data.node_groups['Probe'].interface.items_tree['Mode'].default_value == 'Second'
''', version)
    other = "b52" if version == "b45" else "b45"
    with pytest.raises(subprocess.CalledProcessError):
        run_worker(config, tmp_path, "dump", version=other, input=str(blend), output=str(tmp_path / "wrong"))
    assert not (tmp_path / "wrong").exists()
    imported = tmp_path / "Imported"
    # dump uses the configured native target, including its packed resources.
    from unittest.mock import patch
    with patch.object(importing, "configuration", return_value={**config, "versions": {version: config["targets"][version]}}):
        importing.dump_sources(blend, imported, version)
    assert list(imported.rglob("resources/images.json"))


@pytest.fixture(scope="module")
def probe_library(config, tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("probe-library")
    source = tmp_path / "nodes/Probe"
    script = source / "geometry/geometry/probe.py"
    script.parent.mkdir(parents=True)
    script.write_text('''from omoonodes import geometry as g
from omoonodes.builder import CustomGeometryGroup

class Probe(CustomGeometryGroup):
    _name = 'Probe'
    def _build_group(self, tree):
        value = tree.inputs.float('Value', 1.0, optional_label=True)
        mode = tree.inputs.menu('Mode', 'A')
        result = tree.outputs.float('Result')
        menu_switch = g.MenuSwitch.float(mode, {'A': value, 'B': 10000.0})
        menu_switch.o.output * 0.8 >> result

ASSET = Probe
''')
    write_json(source / "collection.json", {"files": {"Probe.blend": {"source": "geometry"}}})
    workspace = tmp_path / "workspaces"
    libraries.build_staged(config, [source], workspace, tmp_path / "build")
    return tmp_path


@pytest.fixture
def shared(config, probe_library, tmp_path, monkeypatch):
    # Each test edits its own copy of the same native libraries.
    shutil.copytree(probe_library / "nodes", tmp_path / "nodes")
    workspace = shutil.copytree(probe_library / "workspaces", tmp_path / "workspaces")
    source = tmp_path / "nodes/Probe"
    script = source / "geometry/geometry/probe.py"
    monkeypatch.setattr(libraries, "configuration", lambda *args, **kwargs: config)
    return source, script, workspace


@pytest.mark.parametrize("version", ["b45", "b52"])
def test_sync_skips_unchanged_and_shares_compatible_edit(config, shared, tmp_path, version):
    source, script, workspace = shared
    before = source_files(source)
    libraries.sync(source, workspace, version)
    assert source_files(source) == before
    blend = workspace / version / "Probe/Probe.blend"
    native(config, tmp_path, f'''import bpy
bpy.ops.wm.open_mainfile(filepath={str(blend)!r},load_ui=False)
g=bpy.data.node_groups['Probe'];g.interface.items_tree['Value'].default_value=7.0
g.asset_data.author='Editor'
g.asset_data.description='Edited probe'
bpy.data.libraries.write({str(blend)!r},{{g}},fake_user=True,compress=True)
''', version)
    libraries.sync(source, workspace, version)
    assert '7.0' in script.read_text() and 'Editor' in script.read_text()
    assert 'optional_label=True' in script.read_text()
    assert 'ASSET_METADATA = {\n    "description": "Edited probe",\n    "author": "Editor"' in script.read_text()
    assert '.o.output' in script.read_text()
    assert '10000.0' in script.read_text() and '10_000' not in script.read_text()
    assert '0.8' in script.read_text() and '0.800000011920929' not in script.read_text()
    assert not list(source.rglob('*.b52.py'))
    stable = source_files(source)
    libraries.sync(source, workspace, version)
    assert source_files(source) == stable


def test_sync_incompatible_shared_edit_preserves_sources(config, shared, tmp_path):
    source, _, workspace = shared
    blend = workspace / "b52/Probe/Probe.blend"
    native(config, tmp_path, f'''import bpy
bpy.ops.wm.open_mainfile(filepath={str(blend)!r},load_ui=False)
g=bpy.data.node_groups['Probe'];g.nodes.new('FunctionNodeReverseString')
bpy.data.libraries.write({str(blend)!r},{{g}},fake_user=True,compress=True)
''', "b52")
    before = source_files(source)
    with pytest.raises(subprocess.CalledProcessError):
        libraries.sync(source, workspace, "b52")
    assert source_files(source) == before


def test_specific_sync_and_disabled_dependency(config, shared, tmp_path):
    source, script, workspace = shared
    variant = script.with_name("probe.b52.py")
    variant.write_bytes(script.read_bytes())
    original = script.read_bytes()
    blend = workspace / "b52/Probe/Probe.blend"
    native(config, tmp_path, f'''import bpy
bpy.ops.wm.open_mainfile(filepath={str(blend)!r},load_ui=False)
g=bpy.data.node_groups['Probe'];g.nodes.new('FunctionNodeReverseString')
bpy.data.libraries.write({str(blend)!r},{{g}},fake_user=True,compress=True)
''', "b52")
    libraries.sync(source, workspace, "b52")
    assert script.read_bytes() == original
    assert "ReverseString" in variant.read_text()
    variant.write_text("DISABLED = True\n")
    (script.parent / "consumer.py").write_text('''from omoonodes import geometry as g
from omoonodes.builder import CustomGeometryGroup
class Consumer(CustomGeometryGroup):
    _name = 'Consumer'
    def _build_group(self, tree):
        g.Group('Probe')
ASSET = Consumer
''')
    before = blend.read_bytes()
    with pytest.raises(subprocess.CalledProcessError):
        libraries.dev(source, workspace, "b52")
    assert blend.read_bytes() == before


def test_dependency_version_is_rejected_before_export(config, tmp_path):
    owner, dependent = tmp_path / "Owner.blend", tmp_path / "Dependent.blend"
    native(config, tmp_path, f'''import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
g=bpy.data.node_groups.new('Owner','GeometryNodeTree');g.asset_mark()
bpy.data.libraries.write({str(owner)!r},{{g}},fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load({str(owner)!r},link=True) as (a,b): b.node_groups=['Owner']
g=bpy.data.node_groups.new('Dependent','GeometryNodeTree');g.asset_mark()
g.nodes.new('GeometryNodeGroup').node_tree=b.node_groups[0]
bpy.data.libraries.write({str(dependent)!r},{{g}},fake_user=True,compress=True)
''', "b45")
    native(config, tmp_path, f'''import bpy
g=bpy.data.node_groups.new('Owner','GeometryNodeTree');g.asset_mark()
bpy.data.libraries.write({str(owner)!r},{{g}},fake_user=True,compress=True)
''', "b52")
    output = tmp_path / "exported"
    with pytest.raises(subprocess.CalledProcessError) as failure:
        run_worker(config, tmp_path, "dump", version="b45", input=str(dependent), output=str(output))
    assert "Owner.blend" in failure.value.stdout and "saved by Blender 5.2" in failure.value.stdout
    assert not output.exists()


@pytest.mark.parametrize("version", ["b45", "b52"])
def test_imported_classes_keep_links_target_selection_and_sync(config, tmp_path, monkeypatch, version):
    root = tmp_path / 'custom-sources'
    owner = root / 'Owner'
    owner_script = owner / 'defs/custom.py'
    owner_script.parent.mkdir(parents=True)
    definition = '''from omoonodes.builder import CustomGeometryGroup
class SharedRecipe(CustomGeometryGroup):
    _name = 'Shared UV'
    def _build_group(self, tree):
        value = tree.inputs.float('Value', 1.0)
        result = tree.outputs.float('Result')
        value * 2.0 >> result
ASSET = SharedRecipe
'''
    owner_script.write_text(definition)
    owner_script.with_name('custom.b52.py').write_text(definition.replace('* 2.0', '* 3.0'))
    write_json(owner / 'collection.json', {'files': {'Owner.blend': {'source': 'defs'}}})
    extra = root / 'Extra'
    script = extra / 'recipes/geometry/probe.py'
    script.parent.mkdir(parents=True)
    script.write_text('''from nodes.Owner.defs.custom import SharedRecipe
from omoonodes.builder import CustomGeometryGroup
class UsesShared(CustomGeometryGroup):
    _name = 'Uses Shared'
    def _build_group(self, tree):
        value = tree.inputs.float('Value', 4.0)
        result = tree.outputs.float('Result')
        SharedRecipe(Value=value) >> result
ASSET = UsesShared
''')
    write_json(extra / 'collection.json', {'dependencies': ['Owner'], 'files': {
        'Extra.blend': {'source': 'recipes', 'links': {'Shared UV': {'library': 'Owner', 'file': 'Owner.blend'}}}}})
    monkeypatch.setattr(libraries, 'configuration', lambda *args, **kwargs: config)
    workspace = tmp_path / 'workspaces'
    libraries.build_staged({**config, 'versions': {version: config['targets'][version]}},
                           [owner, extra], workspace, tmp_path / 'build')
    blend = workspace / version / 'Extra/Extra.blend'
    native(config, tmp_path, f'''import bpy
bpy.ops.wm.open_mainfile(filepath={str(blend)!r}, load_ui=False)
shared=bpy.data.node_groups['Shared UV']
assert shared.library is not None
assert sum(group.name.startswith('Shared UV') for group in bpy.data.node_groups)==1
math=next(node for node in shared.nodes if node.bl_idname=='ShaderNodeMath')
assert math.inputs[1].default_value=={3 if version == 'b52' else 2}
consumer=bpy.data.node_groups['Uses Shared']
consumer.interface.items_tree['Value'].default_value=7.0
bpy.data.libraries.write({str(blend)!r}, {{consumer}}, fake_user=True, compress=True)
''', version)
    libraries.sync(extra, workspace, version)
    code = script.read_text()
    assert 'from nodes.Owner.defs.custom import SharedRecipe' in code
    assert 'SharedRecipe(' in code and '.Group(' not in code and '7.0' in code
    imported = tmp_path / 'imported/ImportedExtra'
    importing.dump_sources(blend, imported, version)
    code = (imported / 'Extra/geometry/uses_shared.py').read_text()
    assert 'from nodes.Owner.Owner.geometry.shared_uv import SharedUV' in code
    assert 'SharedUV(' in code and '.Group(' not in code


@pytest.mark.parametrize("remote", [False, True])
def test_native_publication_retains_nodes_and_remote_listing(config, shared, tmp_path, remote):
    _, _, workspace = shared
    folder = workspace / "b52/Probe"
    output = tmp_path / "published"
    run_worker(config, tmp_path, "publish", version="b52", input=str(folder), output=str(output), self_contained=True, remote=remote)
    assert (output / "_asset-library-meta.json").exists() == remote
    original = run_worker(config, tmp_path, "inspect", version="b52", input=str(folder / "Probe.blend"))
    published = run_worker(config, tmp_path, "inspect", version="b52", input=str(output / "Probe.blend"))
    assert original["graphs"] == published["graphs"]
