# OmooNodes 项目规范

## 总则

**不管是代码还是文档，遵循「少就是多」的原则，以好理解为首要要求**

- 说明性内容以中文为主，专有名词和约定俗成的表达可使用英文。
- 修改代码、依赖或执行方式后，不保留旧路径、转发函数、兼容层或胶水代码；更新并运行相关测试，不主动构建文档或打包资产。
- 优先选择依赖少、直接、易验证的实现，复用已有函数，避免重复造轮子。
- 避免嵌套结构；特殊、非常规的实现需要注释。
- 确保文件名、文件夹名和内容边界一致。
- 优先使用、提供 Git Bash 命令，Windows 路径使用正斜杠。

## 整理代码

当用户说「整理代码」时，对全局或局部执行：

- 检查并确保代码符合本文提到的所有开发规范。
- 保留已有的其他修改和有效功能，沿真实调用链清理无用代码。
- 同步整理文档，使名称、说明与实际实现一致。
- 精简测试，保留有效行为覆盖，运行全量测试并确认正常退出。

## 查询文档

- [总览](README.md)：项目用途与安装方式。
- [资产库](docs/asset-libraries.md)：资产库使用说明。
- [开发](docs/develop.md)：资产构建、节点往返与文档开发流程。
- [O Essentials](docs/nodes/o-essentials.md)、[O Extra](docs/nodes/o-extra.md)：节点参考。

## 常见命令

```bash
# 安装或同步开发依赖
uv sync

# 运行全部测试
uv run pytest tests

# 从正式节点脚本准备人工编辑库
uv run omoonodes dev nodes/O_Essentials -o workspaces
uv run omoonodes dev nodes/O_Essentials -s workspaces

# 测试文档
uv run docs test

# 构建版本文档到本地 gh-pages
uv run docs build

# 本地预览文档
uv run docs dev

# 部署版本文档到 GitHub gh-pages
uv run docs deploy

# 构建本地资产库
uv run omoonodes build --target b45 -o contents

# 构建独立本地资产库
uv run omoonodes build nodes/O_Extra --target b45 --self-contained -o contents

# 构建远程资产库
uv run omoonodes build --target b52 --remote -o dist

# 首次导入全部 Asset 节点组
uv run omoonodes dump path/to/O_Library.blend -o nodes/O_Library
```

## 命名规范

- 变量、函数、Docstring 使用英文；同一概念在代码和文档中使用统一表达。
- 函数的动作前缀应表达产物边界：`generate_*` 表示 AI 生成，`build_*` 表示代码层构建，`create_*` 表示 Blender 内创建。
- 名称应说明业务职责，并与用户概念、公开协议和界面术语保持一致。
- 文件和目录名表达稳定的业务分类和模块职责，不直接沿用函数名，也不按临时执行步骤命名；集合层使用复数，单项分类使用单数。
- 资产库目录沿用 `O_Essentials`、`O_Extra` 等名称；节点名、Socket 名保留资产原始拼写，例如 `O Solidfy`、`Rest Positon`。
- 资产库压缩包名使用大驼峰，需要标明 Blender 版本时使用 `b45` 等标识，例如 `OmooNodes.v0.1.0.b45.zip`。
- 新增 Blender 类型时，Class 使用大驼峰且不加前缀；Operator 使用动宾结构，Menu、Panel、AddonPreferences、PropertyGroup 使用实际类型后缀。
- 项目内 Blender 类型使用 `omoo` 前缀：Operator 如 `omoo.build_assets`，Menu 如 `OMOO_MT_assets`，Panel 如 `OMOO_PT_assets`，公共自定义 Property 如 `omoo_settings`。Operator 自身 Property 使用业务名称，不加项目前缀。

## 文档规范

- `README.md` 面向用户，实现与构建细节放入 `docs/develop.md`。
- 文档只正面描述当前主题的职责与实现，不记录无关模块、未采用路径、历史差异或边界辩解。
- 修改代码、依赖或执行方式时，按需调整已有文档与计划，不为同一主题新建重复文件。
- 根据内容选择最清晰的表达方式，优先简洁文字；复杂流程或关系在有助于理解时使用图表。Mermaid 流程图默认从上到下，节点标识使用英文字符。
- 不使用 `---` 分割器；一级标题只用于文件开头。
- 节点说明保存在 `docs/nodes/`；不维护节点释义生成器或效果验证脚本。
- `.agents/skills/use-omoo-nodes/references/node-catalog.json` 是 skill 的机器参考，不在 skill 中重复维护节点 Markdown。

## Blender 资产开发规范

- OmooNodes 使用 Blender 原生 Asset Library；正式节点脚本位于 `nodes/`，人工编辑库位于 `workspaces/b45/`、`workspaces/b52/`，本地发布输出使用 `contents/<版本>/`，远程发布输出使用 `dist/b52/`。
- 每个资产库保留一个源目录。无后缀 `.py` 是适配项目最低配置目标的通用实现，`.b52.py` 是 b52 专用完整实现；临时编辑库均包含完整目标内容。
- 支持目标配置在 `pyproject.toml` 的 `tool.omoonodes.targets` 列表，精确版本由 `tool.omoonodes.versions` 覆盖，由 uv 自动准备隔离环境；各目标使用原生 bpy 完成构建、导出与校验，本地与 CI 复用同一流程。
- 保持资产库间的相对路径与公共节点依赖有效。本地构建先处理 `O_Essentials`，再处理依赖它的资产库，并使用同一输出父目录。
- `src/omoonodes/` 是独立可安装的 Python 包，提供 `omoonodes` CLI，读取调用项目配置；后台 worker 使用隔离的 Blender 用户目录。
- 构建在临时目录完成组合、清理与校验，全部成功后替换目标目录；备份文件、旧 Remote listing 和临时文件不进入产物。
- `--self-contained` 用于独立本地资产库；`--remote` 本地化外部引用并生成 listing、metadata、缩略图与 SHA-256，同时传入时按 remote 执行。
- 修改资产或版本合并逻辑后，使用目标 Blender 构建受影响资产库并验证结果；根据改动检查节点接口、依赖和目标版本行为。
- 修改节点接口或功能后，检查目标库接口、依赖与保存重载，运行相关测试；具体步骤见 [开发](docs/develop.md)。
- 节点单元测试保存在 `tests/nodes/`，以 `test_o_<节点名>.py` 命名，直接验证输入与输出；新增或修改功能同步补充正常值与边界断言。工具包测试保存在 `tests/cli/`。
- Deform 分类的节点必须全部有单元测试；优先用少量输入组合验证有效变形、拓扑与作用范围。
- 节点树使用原生节点，保持布局清楚、接口与数据生命周期明确；复用已有公共节点，避免重复实现。
- 节点名称使用简洁的 `O <功能>`，沿用已有节点术语；类名、源码文件名与资产名保持一致。
- 核心参数直接放在接口顶层；次要调节项放入默认折叠的 `Options` 面板。
- 迭代变形节点的 `Iterations` 默认 5、范围 1–20，优先与 `O Smooth` 等同类节点保持一致。
- 每步作用比例使用 `Options / Weight`，Socket 为 Float、subtype 为 `FACTOR`、范围 0–1；默认值按效果选择。
- 用于限制作用范围的 `Selection` 默认 True，设置 `hide_value=True` 和 `hide_in_modifier=True`。
