from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup
from .o_uv_island import OUVIsland


class OTransferMaterial(CustomGeometryGroup):
    _name = "O Transfer Material"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry("Mesh")
        source = tree.inputs.geometry("Source")
        with tree.inputs.panel("Options", default_closed=True):
            uv_island = tree.inputs.menu("UV Island", "Sample Position", expanded=True, optional_label=True)
            uv_island_1 = tree.inputs.integer("UV Island", 0, hide_value=True)
            uv = tree.inputs.string("UV", "UVMap")
        mesh_1 = tree.outputs.geometry("Mesh")

        capture = g.CaptureAttribute.point(geometry=source)
        boolean = capture.items.boolean(g.Boolean(boolean=True), "Boolean")
        evaluate_on_domain = g.SampleIndex.face.integer(source, OUVIsland(UV=uv), g.SampleNearest.face(source)).o.value.face.evaluate()
        menu_switch = g.MenuSwitch.integer(uv_island, {"Sample Position": evaluate_on_domain, "Custom": uv_island_1})
        sample_nearest_surface = g.SampleNearestSurface.integer(source, g.MaterialIndex(), OUVIsland(UV=uv), sample_group_id=menu_switch.o.output)
        (
            g.JoinGeometry(geometry=(capture.o.geometry, mesh))
            >> g.DeleteGeometry.point(selection=boolean.output)
            >> g.SetMaterialIndex(material_index=sample_nearest_surface.o.value)
            >> mesh_1
        )

ASSET = OTransferMaterial

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "304de8ab-a7d3-4df3-b6b2-4674d8814339",
}
