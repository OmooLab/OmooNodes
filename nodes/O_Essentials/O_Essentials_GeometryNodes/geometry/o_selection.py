from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class OSelection(CustomGeometryGroup):
    _name = "O Selection"
    _color_tag = "INPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        name = tree.inputs.string("Name", "")
        invert = tree.inputs.boolean("Invert", False)
        selection = tree.outputs.boolean("Selection")

        repeat_zone = g.RepeatZone(name.find(",").count + 1.0)
        rest = repeat_zone.items.string(name, "Rest")
        boolean = repeat_zone.items.boolean(name="Boolean")
        find_in_string = rest.current.find(",")
        switch = (find_in_string.count > 0).switch.string(rest.current, rest.current.slice(length=find_in_string.first_found))
        named_attribute = g.NamedAttribute.boolean(g.JoinStrings((g.String(string="o_selection"), switch.replace(" ", "")), delimiter=":"))
        (
            rest.current.slice(find_in_string.first_found + 1.0, rest.current.length())
            >> rest.next
        )
        (boolean.current | named_attribute.o.attribute) >> boolean.next
        invert.switch.boolean(boolean.result, ~boolean.result) >> selection

ASSET = OSelection

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
