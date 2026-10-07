# 开发

本页记录 OmooNodes 资产库的构筑与文档开发流程。

## 环境

项目使用 `uv` 管理 Python 环境。

```bash
uv sync
uv run pytest tests
```

构建或预览文档：

```bash
uv run mkdocs build
uv run mkdocs serve
```

## 目录结构

```text
subspaces   Blender 资产源文件
dist        Asset Library 导出文件夹
```

`subspaces` 中每个 Asset Library 只保留一个目录。无版本后缀的 `.blend` 是基础层；
`.b<major><minor>.blend` 是从对应版本起启用的 overlay。同名 Node Group 向下覆盖，
新名称则追加。执行构建的 Blender 自动决定启用哪些 overlay，输出路径不包含版本层。

例如：

```text
subspaces/O_Essentials/
├─ O_Essentials_GeometryNodes.blend
├─ O_Essentials_GeometryNodes.b52.blend
├─ O_Essentials_ShaderNodes.blend
└─ blender_assets.cats.txt
```

Blender 4.5 只构筑基础层；Blender 5.2 会按顺序组合基础层和 `.b52.blend`。overlay 可以
Link 基础文件中的公共 Node Group，构筑脚本会将这些引用映射回产物中的本地数据，并让
overlay 中的同名 Node Group 覆盖基础实现。

### 版本合并规则

- 无后缀文件是 Blender 4.5 基础层，不应创建低于 `b45` 的 overlay。
- 目标版本由执行脚本的 Blender 决定；overlay 的启用版本由 `.b52.blend` 等文件名决定，
  不使用文件内部记录的保存版本。
- 构筑时先载入基础层，再按版本从低到高应用所有不高于目标版本的 overlay。
- overlay 中的新 Node Group 会被加入；同名 Node Group 会覆盖较低版本的实现。

例如 Blender 5.3 的合并顺序为 `base → b52 → b53`，最终由 `b53` 的同名节点胜出。

## 执行构筑脚本

脚本必须由目标 Blender 执行。以下示例使用 Git Bash，并将 executable 保存到变量中：

`build_assets.py` 是单文件工具，只依赖 Blender 内置的 `bpy` 与 Python 标准库。构筑
环境不需要另外安装 Python、`uv` 或项目依赖；分发构筑工具时只需携带该脚本。

```bash
BLENDER="C:/path/to/blender.exe"
```

通用调用形式：

```bash
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- SOURCE [OPTIONS]
```

- `-b`：使用后台模式，不打开 Blender 界面。
- `--python-exit-code 1`：Python 构筑失败时返回非零退出码。
- `-P build_assets.py`：执行构筑脚本。
- `--`：分隔 Blender 参数与构筑脚本参数。
- `SOURCE`：单个 Asset Library 源目录。
- `-o/--out`：输出父目录；产物目录名沿用 `SOURCE` 的目录名。

构筑会在临时目录中完成组合、清理与校验，全部成功后才替换目标目录。Blender 备份文件、
旧 Remote listing 和临时文件不会进入产物。

## 构筑本地资产库

默认本地构筑保留 linked library 和原始相对路径。应先构筑 `O_Essentials`，再构筑
`O_Extra`，并让它们保持在同一输出父目录：

```bash
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Essentials -o contents
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Extra -o contents
```

结果分别位于 `contents/O_Essentials` 和 `contents/O_Extra`。使用 `--self-contained`
可以构筑没有外部 linked library 依赖的独立本地资产库：

```bash
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Extra --self-contained -o contents
```

## 构筑远程资产库

Remote 模式会将 linked datablock 本地化，清理外部引用，生成 listing、metadata 和缩略图，
并校验资产文件与 SHA-256：

本地化会在源文件的相对路径仍然有效时完成。依赖 datablock 会保留节点内容，但不会
继承来源资产库的 Asset 标记。

```bash
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Essentials --remote -o dist
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Extra --remote -o dist
```

结果分别位于 `dist/O_Essentials` 和 `dist/O_Extra`。如需适配网络地址，可在构筑完成后
手动调整发布目录名。

Remote 构筑会验证资产数量、文件数量、缩略图和 SHA-256。`--remote` 已经生成无外部引用
的产物，因此不能与 `--self-contained` 同时使用。

## 节点文档与 Codex Skill

节点资料采用一套单向同步流程：

```text
发布版 .blend
  → .agents/skills/use-omoo-nodes/references/node-catalog.json
  → docs/nodes/o-essentials.md
  → docs/nodes/o-extra.md
```

`node-catalog.json` 是 skill 使用的机器参考，保存精确节点名、类型、Socket identifier、
默认值、依赖和简短用途。`docs/nodes/` 是从同一 catalog 生成的面向用户参考。不要在 skill
中再维护重复的节点 Markdown。

节点功能、妙用案例和参数释义集中维护在 `scripts/generate_node_reference.py`，其中节点功能
同时写回 catalog 的 `description`，docs 则生成面向使用者的完整说明。更新资产后先用目标
Blender 重新检查发布版，再生成 catalog 描述和 docs：

```bash
BLENDER="C:/path/to/blender.exe"

"$BLENDER" -b --python-exit-code 1 \
  -P scripts/inspect_omoo_nodes.py -- \
  dist/O_Essentials dist/O_Extra \
  --output .agents/skills/use-omoo-nodes/references/node-catalog.json

uv run python scripts/generate_node_reference.py \
  .agents/skills/use-omoo-nodes/references/node-catalog.json \
  dist \
  docs/nodes
```

生成器会把 `BEHAVIOR_NOTES` 同步写入 catalog 的 `description`，并同时重建两份节点文档。
新增节点但缺少用途说明时生成会失败，避免 skill 与 docs 静默漂移。

最后运行 Blender 集成检查、skill validator、测试和文档构筑：

```bash
"$BLENDER" -b --python-exit-code 1 \
  -P scripts/validate_omoo_nodes_in_blender.py -- \
  dist dist/validation/use-omoo-nodes-validation.blend
uv run pytest tests/test_use_omoo_nodes_skill.py
uv run mkdocs build
```

文档中的节点名必须保留资产原始拼写，例如 `O Solidfy` 与 `Rest Positon`。
