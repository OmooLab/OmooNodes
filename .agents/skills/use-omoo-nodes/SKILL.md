---
name: use-omoo-nodes
description: 使用 Omoo Nodes 和 Blender 原生节点实现 Geometry Nodes、Shader、Compositor 等节点效果。用于动态、程序化建模、字段、属性、实例和模拟任务；严格限定工作范围，并交付命名原生、布局清楚、便于继续编辑的节点树。
---

# Use Omoo Nodes

把「效果正确」「节点可读」作为同等重要的交付目标。

## 范围

- 只完成用户要求的节点效果。动态任务只实现动态本身，不要创建或调整相机、灯光、背景、
  布景、渲染设置，也不要为展示效果添加无关对象。
- 仅创建效果成立所必需的几何、材质或辅助数据；修改既有文件前先检查目标对象和节点树，
  保留用户已有结构。
- 优先选择步骤少、语义直接的方案。复用真正的 Omoo Nodes 资产；原生节点更清楚时使用原生
  节点，不要重建近似资产。

## 使用 Omoo Nodes

先读取 Blender 版本和 `bpy.context.preferences.filepaths.asset_libraries`。资产版本不得
高于 Blender。Blender 5.2 远程库：

| 资产库 | URL |
| --- | --- |
| `O Essentials` | `https://assets.omoolab.xyz/b52/O_Essentials` |
| `O Extra` | `https://assets.omoolab.xyz/b52/O_Extra` |

其他 Blender 版本只使用已经发布的匹配地址，不要猜测 URL。首次使用远程资产时，若缓存中
没有目标 `.blend`，先在 Asset Browser 加载。

在 [node-catalog.json](references/node-catalog.json) 中搜索名称或 `description`，根据
`tree_type`、`interface`、`dependencies` 和实际 `.blend` 选择节点；仓库内有对应内容时再
查看 `docs/nodes/`。不要维护自然语言到节点名称的固定映射。

使用 [omoo_blender.py](scripts/omoo_blender.py) 的
`ensure_omoo_node_group`、`add_geometry_modifier`、`add_group_node`、
`set_modifier_input` 和 `set_group_node_input`。默认 append；只有用户明确要求时才 link。

## 构建节点

- 动画优先用 Scene Time、Driver 或可重算字段；只有确实需要历史状态时才使用
  Simulation Zone。验证至少两个不同帧。
- 明确 Field 的求值 Geometry、Domain、数据类型和坐标空间。拓扑变化后不要依赖 Index；
  需要稳定随机或跨帧对应时使用稳定 ID。
- 尽量保留 Instance，仅在后续操作需要真实几何时 Realize Instances。只在跨阶段、跨 Zone
  或拓扑变化后仍需数据时 Capture Attribute。
- 所有新建的自定义 Attribute 使用 `o_` 前缀，例如 `o_particle_color`；存储、读取和材质
  引用必须使用同一名称。
- Blender 5.2 创建 Geometry Nodes modifier 节点树时，先设置
  `node_group.is_modifier = True`，再创建接口。
- 只暴露用户需要调节的 Group Input，并设置合理默认值、范围和单位。

## 保持可读

- 保留功能节点的默认显示名，不要修改其 `name` 或设置 `node.label`。读者必须能直接看出
  使用了哪个 Blender 或 Omoo 节点。
- 主数据流从左到右。移动节点消除交叉线和穿过节点的连线；必要时使用少量 Reroute。
- 不要让任何节点、Reroute、Frame 或说明节点互相重叠；布局后缩放查看整棵节点树再检查。
- 距离较远但使用相同接口时，在消费节点附近创建多个 Group Input。每个 Group Input 实例
  只显示本地已连接的输出 Socket；完成连线后隐藏其余 Socket：

  ```python
  for socket in group_input.outputs:
      if hasattr(socket, "hide"):
          socket.hide = not socket.is_linked
  ```

- Frame 和 String 说明不是默认要求。只对结构复杂、仅靠节点和连线难以理解的局部使用
  Frame；Frame 保持默认颜色。只有确有补充信息时才加入 String，内容必须非空并说明原理、
  关键参数或限制；空 String 直接删除。

## 验收

- 在时间线或 viewport 验证目标效果和代表性帧，不通过搭景、打光或渲染包装结果。
- 检查节点名称未改、无重叠、无不必要的交叉或长线、Group Input 未连接 Socket 已隐藏、
  自定义 Attribute 均以 `o_` 开头。
- 最终只汇报实现机制、可调参数和验证结果，不扩展到用户未要求的工作。
