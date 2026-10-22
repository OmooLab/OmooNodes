# 开发

## 环境与配置

```bash
uv sync --locked --dev
uv run pytest tests
```

本仓库同时维护节点资产库和 `omoonodes` Python 包。`src/omoonodes/` 提供 `omoonodes` 命令，读取调用项目的 `pyproject.toml`：

```toml
[tool.omoonodes]
targets = ["b45", "b52"]
```

默认 b45 使用 Python 3.11 / bpy 4.5.14，b52 使用 Python 3.13 / bpy 5.2.2。
uv 在 `.cache/nodes/` 准备各目标环境；构建、导出、保存和校验均使用对应 bpy。
`tool.omoonodes.versions` 可覆盖已声明目标的精确 bpy 版本。输入库及依赖的保存主次版本须与目标一致。

各指令以 `...` 显示进度、`✔` 标记完成，最后列出输出目录。Blender 的 Info、Warning、读取路径和正常退出时的内存泄漏统计隐藏；其他 Error 或异常退出会停止后续流程。

## 节点开发

`nodes/<资产库>/` 保存 Python、资源、catalog 和记录文件归属与依赖的 `collection.json`。
通用实现使用 `.py`，b52 专用实现使用完整的 `.b52.py`；专用文件内 `DISABLED = True` 表示停用。同版本的依赖库放在同一父目录。
源码沿用 nodebpy 的节点类、Socket 运算和 `>>` 连线写法，导入包名为 `omoonodes`；最小示例见工具包的 `src/omoonodes/README.md`。
跨库节点通过 `from nodes.<库>.<源目录>... import 节点类` 引用；CLI 加载当前目标的源码，并按 `collection.json` 复用外部链接。
`dev`、`build` 自动布局，统一使用无 Frame 的节点布局；源码不记录节点位置和布局开关。
布局先排列计算节点，再按消费者的位置拆分 Group Input：同列相邻且整体紧凑的消费者共用输入，跨列或相距较远的消费者分别读取。几何、材质、合成树使用同一规则。无障碍的独立连线保持直连，共享长连线和避障连线使用 reroute。

```bash
# 首次导入 Asset 节点及依赖，输出目录须不存在
uv run omoonodes dump path/to/O_Library.blend -o nodes/O_Library

# 从源码生成并覆盖开发库
uv run omoonodes dev nodes/O_Extra -o workspaces

# 从开发库回写修改后的 Python 和资源
uv run omoonodes dev nodes/O_Extra -s workspaces

# 构建本地库及依赖
uv run omoonodes build nodes/O_Extra --target b45 -o contents

# 独立本地库：嵌入外部依赖
uv run omoonodes build nodes/O_Extra --target b45 --self-contained -o contents

# 远程库：嵌入依赖并生成原生 listing、metadata、缩略图和 SHA-256
uv run omoonodes build --target b52 --remote -o dist
```

人用 Blender 编辑开发库，AI 直接修改源码，由操作者决定覆盖方向。同步跳过未修改内容，已有专用实现回写专用文件；共享修改通过所有继承目标的原生构建验证后覆盖基础文件，失败时保留源码。b52 删除共享节点时写入停用文件。
更新公共库时，输出目录中已有的引用库须一并重建；CLI 根据依赖关系检查并提示选择共同的源码目录。先同步需要保留的人工修改，再执行 `dev` 或 `build`。导出、同步和发布会检查 Menu 的选项是否有效。
结构验证不代替效果检查；修改功能后检查接口、依赖和实际输出。
`dev` 默认最低目标，`build` 默认全部目标；`-s` 自动选择唯一工作区目标，多版本时需指定 `--target`。
省略来源时读取 `tool.omoonodes.source`，默认 `nodes`。默认输出分别为 `workspaces/<目标>/<资产库>/` 和 `dist/<目标>/<资产库>/`。
构建在临时目录完成，目标 Blender 保存、重载检查后替换输出；CI 再压缩发布。


## 测试

`tests/cli/` 验证工具包，`tests/nodes/<资产库>/<树类型>/test_o_<节点名>.py` 验证单个节点的输入与输出。

```bash
uv run pytest tests
uv run pytest tests/cli
uv run pytest tests/nodes
uv run pytest tests/nodes --node-target b45 -k o_mix_color
uv run pytest tests/nodes/O_Essentials/geometry/test_o_blend.py
```

每个节点一个普通 pytest 文件，直接写输入、调用和断言；需要多组输入时使用 `pytest.mark.parametrize`。新增测试文件即可被发现。当前覆盖 14 个节点，其中 Deform 类 9 个全部覆盖，目录检查防止漏测。

`conftest.py` 负责双目标启动：复用现有 bpy 环境和目标源码选择，在目标环境准备 pytest；每个节点独立进程执行，每项测试前清空 Blender 数据并直接创建被测节点及依赖。失败直接显示原生 pytest 输出；单节点执行超时为 120 秒，CI 保留日志和图像。

共用的 `evaluation.py` 仅提供小型输入数据、实际求值和数值比较。几何与字段读取 depsgraph 输出，Shader 和 Compositor 读取 CPU 求值的线性 EXR。期望值来自独立计算或明确的节点约定，浮点比较声明容差。

| 节点 | 已测行为 | 待补范围 |
| --- | --- | --- |
| O Mix Color | RGBA 插值端点、中点和逐点 Factor | 越界 Factor |
| O Resample Edge | 整除及非整除间距、端点、独立曲线选择 | 闭合边、分叉和属性传递 |
| O Smooth | 中心凸起平滑、对称性、拓扑计数、零权重和局部选择 | 多次迭代、Pin Sharp、Pin Boundary |
| O Project | 最近点、双向射线命中、距离外未命中、半权重和局部选择 | Radius Offset、Source/Normal 方向和方向权重 |
| O Linear | 已知向量渐变、0.5 阈值两侧和旋转 | 隐式坐标输入 |
| O Stroke | Matte 描边、平方 Alpha、全透明、光照下的 Alpha、关闭描边和位移恢复 | Depth/Normal 边缘及光照调色的 RGB |
| O Random Jitter | 零强度、有效位移、固定帧重复性和跨库依赖 | 时间步进与参数范围 |
| O Blend | 按索引半权重混合、局部选择、零系数和拓扑保持 | 不同点数的源几何 |
| O Curve Deform | 沿折线拟合、半权重、局部选择、零权重和拓扑保持 | 截面朝向、Tilt、多曲线及闭合曲线 |
| O Displace | 法线及向量位移、Midlevel、局部选择、零强度和拓扑保持 | 逐点位移场 |
| O Point Deform | Rest Positon 位移传递、半权重、局部选择、零权重和拓扑保持 | 非均匀源变形和平滑参数 |
| O Relax | 平面不均匀网格松弛、局部选择、零权重和拓扑保持 | 自定义投射面、多岛及多次迭代 |
| O Sharpen | 曲率对称网格的非零位移、固定边界、零权重和拓扑保持 | 曲率菜单、局部选择及多次迭代 |
| O Transform | 缩放、旋转、平移组合、局部选择、空选择和拓扑保持 | Matrix 与软选择 |

O Resample Edge 沿用 Blender 的 [Length 重采样语义](https://docs.blender.org/manual/en/4.0/modeling/geometry_nodes/curve/operations/resample_curve.html)：Length 为近似间距，样本均匀分布。长 2、Length=0.75 的直线得到位置 0、1、2。

## 发布 Python 包

`.github/workflows/test.yml` 在推送 main 或提交面向 main 的 PR 时运行测试、打包，并验证 wheel 和源码包的最小节点构建、导出和重新构建。

`.github/workflows/publish.yml` 在推送 `cli-v*` 标签时运行测试、构建源码包和 wheel，分别安装后在临时项目中验证最小节点的构建、导出和重新构建，再通过 PyPI Trusted Publishing 发布 `omoonodes`。包版本读取 `pyproject.toml`。

首次发布前，在 GitHub 仓库创建 `pypi` environment，再到 [PyPI Publishing](https://pypi.org/manage/account/publishing/) 添加 pending publisher：

| 字段 | 值 |
| --- | --- |
| PyPI Project Name | `omoonodes` |
| Owner | `OmooLab` |
| Repository name | `OmooNodes` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

首次成功上传会自动创建 PyPI 项目，无需配置 API token。提交版本和锁文件后，推送对应标签，例如：

```bash
git tag cli-v0.1.0
git push github cli-v0.1.0
```

节点库独立使用 `nodes-v*` 标签，触发 `.github/workflows/release.yml`，通过 matrix 并行构建 b45 本地库和 b52 远程库，各自完成后将压缩包上传同一个 GitHub Release：

```bash
git tag nodes-v0.1.0
git push github nodes-v0.1.0
```

节点库版本由标签决定，压缩包沿用 `OmooNodes.v0.1.0.b45.zip` 格式；两类发布分别触发、独立版本。

## 文档

```bash
uv run python -m tools.docs test    # 临时目录严格构建
uv run python -m tools.docs dev     # 本地预览
uv run python -m tools.docs build  # 按 major.minor.x 构建并提交到本地 gh-pages
uv run python -m tools.docs deploy # 推送到 github 远端
```

节点说明在 `docs/nodes/`，机器参考在 `.agents/skills/use-omoo-nodes/references/node-catalog.json`。
