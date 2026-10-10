# Node-group asset "O Voxel Remesh" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from .o_relax import ORelax


class OVoxelRemesh(CustomGeometryGroup):
    _name = "O Voxel Remesh"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 180, "is_modifier": True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry("Mesh")
        resolution = tree.inputs.float("Resolution", 0.10000000149011612, min_value=0.009999999776482582, max_value=0.10000000149011612)
        relax_iterations = tree.inputs.integer("Relax Iterations", 2, min_value=1, max_value=10)
        with tree.inputs.panel("Options", default_closed=True):
            shade_smooth = tree.inputs.boolean("Shade Smooth", True)
            relax_weight = tree.inputs.float("Relax Weight", 1.0, description="Relative mix weight of neighboring elements", min_value=0.0, max_value=1.0, subtype="FACTOR")
            threshold = tree.inputs.float("Threshold", 0.10000000149011612, description="Values larger than the threshold are inside the generated mesh", min_value=0.0, max_value=1.0)
            adaptivity = tree.inputs.float("Adaptivity", 0.0, min_value=0.0, max_value=1.0, subtype="FACTOR")
            topo_rotation = tree.inputs.rotation("Topo Rotation", (0.0, 0.0, 0.0))
        mesh_1 = tree.outputs.geometry("Mesh")

        transform_geometry = (
            mesh
            >> g.TransformGeometry(rotation=topo_rotation)
            >> g.TransformGeometry(translation=resolution)
            >> g.MeshToVolume(voxel_size=resolution, interior_band_width=resolution * 1.0, resolution_mode="Size", voxel_amount=12.0)
            >> g.VolumeToMesh(voxel_size=resolution, threshold=threshold, adaptivity=adaptivity, resolution_mode="Size", voxel_amount=12.0)
            >> g.TransformGeometry(translation=resolution * -1.0)
            >> g.TransformGeometry(rotation=topo_rotation.invert())
        )
        (
            ORelax(Geometry=transform_geometry, Iterations=relax_iterations, Weight=relax_weight, **{"Max Distance": resolution * 2.0}, _named_links=[("Source", "Custom"), ("Source", mesh)])
            >> g.SetShadeSmooth.face(shade_smooth=shade_smooth)
            >> mesh_1
        )

ASSET = OVoxelRemesh

ASSET_METADATA = {
    "description": "Convert a Polygon Mesh into a Volume and back into Polygons",
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "0218b41f-9d3f-4dd0-9491-5c56e57678db",
}
