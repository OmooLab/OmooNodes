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
- [开发](docs/develop.md)：资产构建、版本合并与节点参考同步流程。
- [O Essentials](docs/nodes/o-essentials.md)、[O Extra](docs/nodes/o-extra.md)：从 catalog 生成的节点参考。

## 常见命令

```bash
# 安装或同步开发依赖
uv sync

# 运行全部测试
uv run pytest tests

# 构建文档
uv run mkdocs build

# 本地预览文档
uv run mkdocs serve

# 指定目标 Blender 的实际路径
BLENDER="C:/path/to/blender.exe"

# 构建本地资产库，先构建公共依赖
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Essentials -o contents
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Extra -o contents

# 构建远程资产库
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Essentials --remote -o dist
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Extra --remote -o dist

# 从发布资产提取节点 catalog
"$BLENDER" -b --python-exit-code 1 -P scripts/inspect_omoo_nodes.py -- \
  dist/O_Essentials dist/O_Extra \
  --output .agents/skills/use-omoo-nodes/references/node-catalog.json

# 同步节点说明与参考文档
uv run python scripts/generate_node_reference.py \
  .agents/skills/use-omoo-nodes/references/node-catalog.json dist docs/nodes

# Blender 集成验证
"$BLENDER" -b --python-exit-code 1 \
  -P scripts/validate_omoo_nodes_in_blender.py -- \
  dist dist/validation/use-omoo-nodes-validation.blend
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
- 节点功能、案例和参数释义集中维护在 `scripts/generate_node_reference.py`；通过生成器更新 catalog 描述与 `docs/nodes/`，不直接修改生成的节点文档。
- `.agents/skills/use-omoo-nodes/references/node-catalog.json` 是 skill 的机器参考，不在 skill 中重复维护节点 Markdown。

## Blender 资产开发规范

- OmooNodes 使用 Blender 原生 Asset Library；资产源文件位于 `subspaces/`，本地构建输出使用 `contents/`，远程构建输出使用 `dist/`。
- 每个资产库保留一个源目录。无版本后缀的 `.blend` 是 Blender 4.5 基础层，`.b52.blend` 等文件是从对应版本起启用的 overlay，不创建低于 `b45` 的 overlay。
- 目标版本由执行构建脚本的 Blender 决定；先载入基础层，再按版本从低到高应用不高于目标版本的 overlay。同名 Node Group 覆盖，新名称追加。
- 保持资产库间的相对路径与公共节点依赖有效。本地构建先处理 `O_Essentials`，再处理依赖它的资产库，并使用同一输出父目录。
- `build_assets.py` 仅依赖 Blender 内置 `bpy` 与 Python 标准库，构建环境无需安装项目 Python 依赖。
- 构建在临时目录完成组合、清理与校验，全部成功后替换目标目录；备份文件、旧 Remote listing 和临时文件不进入产物。
- `--self-contained` 用于独立本地资产库；`--remote` 本地化外部引用并生成 listing、metadata、缩略图与 SHA-256，两者不能同时使用。
- 修改资产或版本合并逻辑后，使用目标 Blender 构建受影响资产库并验证结果；根据改动检查节点接口、依赖和目标版本行为。
- 修改节点接口或功能后，从构建资产重新提取 catalog，运行节点参考生成器、Blender 集成验证与相关测试；具体步骤见 [开发](docs/develop.md)。
- 节点树使用原生节点，保持布局清楚、接口与数据生命周期明确；复用已有公共节点，避免重复实现。
- 新增或修改 Blender 类型时，检查注册与逆序注销；声明式消费者引用类型的 `bl_idname`，`bpy.ops` 执行调用保持原生命名空间写法。
- 操作 Blender 节点效果时遵循项目中的 [use-omoo-nodes skill](.agents/skills/use-omoo-nodes/SKILL.md)。
