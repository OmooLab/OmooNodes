# 开发

## 环境与配置

```bash
uv sync --locked --dev
uv run pytest tests
```

`tools/nodes/` 提供 `nodes` 命令，读取调用项目的 `pyproject.toml`：

```toml
[tool.nodes]
targets = ["b45", "b52"]
```

默认 b45 使用 Python 3.11 / bpy 4.5.14，b52 使用 Python 3.13 / bpy 5.2.2。
转换后端使用 Python 3.13 / bpy 5.2.2 / nodebpy 520.34.1，由 uv 准备环境并缓存到 `.cache/nodes/`。
`tool.nodes.versions` 可覆盖已声明目标的 bpy 版本，`tool.nodes.backend` 可覆盖后端版本。

各指令以 `...` 显示进度、`✔` 标记完成，最后列出输出目录。Blender 的 Info、Warning、读取路径和正常退出时的内存泄漏统计隐藏；其他 Error 或异常退出会停止后续流程。

## 节点开发

`nodes/<资产库>/` 保存 Python、资源、catalog 和记录文件归属与依赖的 `collection.json`。
通用实现使用 `.py`，b52 专用实现使用 `.b52.py`。同版本的依赖库放在同一父目录。

```bash
# 首次导入 Asset 节点及依赖，输出目录须不存在
uv run nodes dump path/to/O_Library.blend -o nodes/O_Library

# 从源码生成并覆盖开发库
uv run nodes dev nodes/O_Extra -o workspaces

# 从开发库完整导出，覆盖对应 Python 和资源
uv run nodes dev nodes/O_Extra -s workspaces

# 构建本地库及依赖
uv run nodes build nodes/O_Extra --target b45 -o contents

# 独立本地库：嵌入外部依赖
uv run nodes build nodes/O_Extra --target b45 --self-contained -o contents

# 远程库：嵌入依赖并生成原生 listing、metadata、缩略图和 SHA-256
uv run nodes build --target b52 --remote -o dist
```

人用 Blender 编辑开发库，AI 直接修改源码，由操作者决定覆盖方向。回写也会删除已移除节点的生成源码。
`dev` 默认最低目标，`build` 默认全部目标；`-s` 自动选择唯一工作区目标，多版本时需指定 `--target`。
省略来源时读取 `tool.nodes.source`，默认 `nodes`。默认输出分别为 `workspaces/<目标>/<资产库>/` 和 `dist/<目标>/<资产库>/`。
构建在临时目录完成，目标 Blender 保存、重载检查后替换输出；CI 再压缩发布。

b52 的 92 个资产已通过完整往返。b52 后端读取 b45 文件时会迁移 `O Stroke`、`O Mix Color` 等节点；完整往返建议使用 `--target b52`。

## 文档

```bash
uv run docs test    # 临时目录严格构建
uv run docs dev     # 本地预览
uv run docs build  # 按 major.minor.x 构建并提交到本地 gh-pages
uv run docs deploy # 推送到 github 远端
```

节点说明在 `docs/nodes/`，机器参考在 `.agents/skills/use-omoo-nodes/references/node-catalog.json`。
