# 统一 nodes 工具

## 核心

`src/nodes_tool/` 是独立安装包，提供原生 `.py ↔ .blend` 和现有 nodes CLI。OmooNodes 的 `nodes/` 是消费项目，不随工具分发。

构建器、节点包装和表达式导出器改编自 nodebpy 520.34.1，保留 `CustomGeometryGroup._build_group`、`g.Raycast.float(...)`、Socket 运算和 `>>`。接口兼容 Python 3.11；不依赖 nodebpy 运行时。保留现有布局、库归属、资源和发布实现。

```python
from nodes_tool.builder import CustomGeometryGroup

class Example(CustomGeometryGroup):
    _name = 'Example'

    def _build_group(self, tree):
        value = tree.inputs.float('Value', 1.0)
        value * 2.0 >> tree.outputs.float('Result')

ASSET = Example
```

源码保存接口、节点运算、有效属性、连线、资源和资产信息。`dev`、`build` 自动布局；导出移除布局 Frame、合并布局产生的 Group Input，并绕过连通 Reroute，不记录节点位置或布局开关。

## 版本

每个目标使用自身 bpy 构建、导出和保存重载校验；输入及依赖库的保存主次版本必须匹配。uv 自动准备隔离运行环境，CLI 导入不加载 Blender。

工具内部处理能准确对应的原生差异，例如属性与菜单插口、Gamma 类型和 Displace 位移缩放。无法对应的节点或参数明确报错。

`.py` 是最低目标的共享实现；只有功能确实无法共享时才使用完整 `.b52.py`。专用文件内 `DISABLED = True` 表示该版本停用。

## 命令

- `dev`：源码构建为人工编辑库，覆盖目标 `.blend`。
- `dev -s`：同版本编辑库导出为 nodebpy 写法；无变化跳过，共享修改验证所有继承目标后覆盖 `.py`，已有专用实现回写专用文件。
- `dump`：从同版本现有资产库导入源码、资源和依赖。
- `build`：构建、校验并发布本地或远程资产库。

流程在临时目录完成，成功后替换输出。Blender Info、Warning、读取路径和正常退出时的内存泄漏统计隐藏，其他 Error 与异常退出阻断。

## 验证

少量真实 Blender 用例覆盖动态插口、Zone、重复菜单、图片材质、跨库引用、版本拒绝和共享回写。项目资产在两个版本分别构建并连续三轮 dev/sync，另检查 O Mix Color、O Stroke、O Project 的实际输出。结构验证不代替效果验证。
