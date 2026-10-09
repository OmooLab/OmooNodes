from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class OGeometryInfo(CustomGeometryGroup):
    _name = 'O Geometry Info'
    _color_tag = 'INPUT'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry('Geometry')
        size = tree.outputs.float('Size')
        center_point = tree.outputs.vector('Center Point')
        median_point = tree.outputs.vector('Median Point')
        realize_instances = g.RealizeInstances(geometry=geometry, realize_to_point_domain=True)
        bounding_box = g.BoundingBox(geometry=realize_instances)
        vector_math = g.Position().o.position.point.total() / g.DomainSize(geometry=realize_instances).o.point_count
        attribute_statistic = g.AttributeStatistic.point.vector(realize_instances, attribute=vector_math)
        vector = bounding_box.o.max - bounding_box.o.min
        vector.x.max(vector.y).max(vector.z) >> size
        (bounding_box.o.min + bounding_box.o.max) * 0.5 >> center_point
        attribute_statistic >> median_point
ASSET = OGeometryInfo
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '99c91009-1ea6-4fc1-bf33-6351786a8df1'}
