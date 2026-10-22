# OmooNodes

`omoonodes` 提供 Python API 和 `omoonodes` 命令，用于 Blender 4.5、5.2 节点的 `.py ↔ .blend` 转换与资产库构建。

在消费项目中安装本仓库的固定提交：

```bash
uv add --dev "omoonodes @ git+https://github.com/OmooLab/OmooNodes.git@<commit>"
```

将 `<commit>` 替换为完整提交 SHA，并提交 `pyproject.toml` 和 `uv.lock`。CI 使用 `uv sync --locked` 安装同一版本。

安装后，在消费项目的 `pyproject.toml` 中配置：

```toml
[tool.omoonodes]
targets = ["b45", "b52"]
source = "nodes"
```

`uv run omoonodes dev` 生成最低目标的人工编辑库，`uv run omoonodes dev -s workspaces --target b45` 回写源码，`uv run omoonodes build` 构建资产库。`uv run omoonodes dump library.blend -o nodes/Library --target b45` 导入已有库。uv 自动准备对应 bpy；输入库必须与目标主次版本一致。

每个库的 `collection.json` 指定源目录：

```json
{"files": {"Library.blend": {"source": "geometry"}}}
```

在 `nodes/Library/geometry/example.py` 中编写：

```python
from omoonodes import TreeBuilder
from omoonodes.builder import CustomGeometryGroup

class Example(CustomGeometryGroup):
    _name = 'Example'

    def _build_group(self, tree: TreeBuilder):
        value = tree.inputs.float('Value', 1.0)
        result = tree.outputs.float('Result')
        value * 2.0 >> result

ASSET = Example
```

沿用 nodebpy 的节点类、Socket 运算和 `>>` 连线写法。`tree.tree`、`node.node` 可直接访问 bpy；原生差异由工具处理。`dev`、`build` 自动布局，源码不记录节点位置或布局开关。

`ASSET_METADATA` 按字段换行，顺序为 description、author、copyright、license、catalog_id、tags，省略空字段。浮点数使用保持 Blender 精度的简短十进制，不加数字分隔符。接口的 `optional_label` 在 5.2 控制标签显示，4.5 往返时保留此设置。

每个需要回写的节点组或材质占一个 `.py`。未修改的手写代码保持原样，修改后仍导出为 nodebpy 写法。Blender 脚本可直接调用 `omoonodes.assets.build_library` 和 `omoonodes.export.dump_library`。

材质类的 `_name` 与 `MATERIAL_NAME` 使用实际材质名。`MATERIAL_PROPERTIES` 按字段换行，记录 Blender 原生材质设置；插件附加的自定义属性不参与回写。

跨库也使用类导入，例如 `from nodes.Library.geometry.example import Example`。`nodes` 指向当前目标选出的源码根目录；`collection.json` 的 dependencies、links 指定构建顺序和外部链接，调用导入的类时复用已链接的节点组。
更新公共库时，输出目录中已有的引用库须一并重建；`dev`、`build` 会检查依赖并提示选择共同的源码目录。人工编辑后先同步源码，再重建相关库。

`.py` 是共享基础，`.b52.py` 是完整专用实现，`DISABLED = True` 表示停用。同步跳过未修改的内容；共享修改必须通过所有继承目标的原生构建验证，失败时保留源码。验证结构保真，效果由项目验证。
