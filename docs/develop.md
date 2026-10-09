# 开发

## 环境

```bash
uv sync --locked --dev
uv run pytest tests
```

`tools/nodes/` 在本项目维护通用 `nodes` CLI。
项目环境使用 Python 3.11、bpy 4.5.14，不安装 nodebpy。
独立后端默认 Python 3.13、nodebpy 520.34.1、bpy 5.2.2，可省略 `tool.nodes.backend`，
也可在该表中覆盖需要的字段。`tool.nodes.targets` 必须明确声明目标及精确 bpy 版本：

```toml
[tool.nodes.targets]
b45 = "4.5.14"
b52 = "5.2.2"
```

工具匹配对应 Python：b45 使用 3.11，b52 使用 3.13。只声明 b45 时，不会补入 b52。
工具通过 uv 准备隔离环境，缓存到 `.cache/nodes/`。后端负责转换和布局，各目标负责检查、
保存、重载与发布清理。worker 使用隔离的 Blender 用户目录。

## 节点来源

当前 `nodes/` 只管理 `O_Essentials` 与 `O_Extra`。

`nodes/<集合>/` 保存 nodebpy 原生 Python、资源、catalog 和 `collection.json`。
无版本后缀 `.py` 是最低支持 b45 的通用实现；`.b52.py` 是 b52 专用完整实现，构建 b52 时优先选择。
同版本的资产库保持在同一父目录，跨库依赖由所属库维护。

## 命令

```bash
# 查看完整参数
uv run nodes --help

# 首次导入全部 Asset 节点组及辅助依赖，不覆盖已有来源
uv run nodes dump path/to/O_Library.blend -o nodes/O_Library

# 准备完整节点库，供 Blender 查看、修改和调试
uv run nodes dev nodes/O_Extra -o workspaces

# 检查并回写人工修订
uv run nodes dev nodes/O_Extra --sync workspaces

# 直接从源码构建本地节点库，自动构建依赖
uv run nodes build nodes/O_Extra --target b45 -o contents

# 外部依赖嵌入库，供独立本地分发
uv run nodes build nodes/O_Extra --target b45 --self-contained -o contents

# 构建远程库，自动嵌入依赖并生成原生 listing
uv run nodes build --target b52 --remote -o dist
```

`dev/build` 省略来源时读取 `tool.nodes.source`，默认 `nodes`；省略目标时处理全部配置目标。
目标版本读取 `pyproject.toml` 的 `tool.nodes.targets`，可用 `--target b52` 只处理一个目标。
`dev` 显示依赖集合、构建与布局、目标版本保存、重载校验，成功后列出最终输出目录。
运行提示使用英文，每个文件显示一行构建、保存和校验流程。
同步显示修改检查、导出、版本合并、重建校验与提交，完成后列出已更新的源码目录。
已知后端转存到较旧目标时收起版本警告，随后重载检查文件版本与节点结构；其他版本警告保留。
资产文件没有场景或界面时产生的空场景提示，以及普通读取日志会收起；失败时显示完整诊断。
`dev` 默认输出 `workspaces/<目标>/<集合>/`，`build` 默认输出 `dist/<目标>/<集合>/`。
可以直接修改源码后 build，人工往返是可选环节。长线使用同高水平通道，保留便于编辑的多个 Group Input。

`dump` 统一导入无版本后缀 `.py`，原文件保存版本只记录来源；目标兼容性由后续 dev/build 检查。
历史普通组先在迁移副本中标记 Asset，再导入。已有来源的修订使用 dev --sync。

回写比较节点逻辑、Asset 元数据、接口标识及 packed 图片内容/颜色设置，忽略布局变化。
仅公共依赖变化时更新基线，不重写消费者源码。共享资源须在所有配置目标一致修改，否则报冲突。
校验源基线、依赖和重建结果，并在提交前再次检查源码和开发库摘要，保护并发编辑。
正式构建使用独立临时目录，不覆盖人工编辑库，选定目标全部成功后才替换产物。
Remote 生成器来自固定 bpy 的原生模块，验证 listing、metadata、文件与 SHA-256。

## CI 与发布

标签发布先运行测试，再分别 build b45 本地库和 b52 远程库，最后由 CI 压缩各目标目录。
Granules 的缺失依赖仍待处理，不参与构建。自定义图标恢复暂缓。
跨版本 Mix 转换仍需验收，保存重载检查不能宣告全部功能兼容。

## 文档

```bash
uv run docs test
uv run docs build
uv run docs dev
uv run docs deploy
```

`test` 在临时目录严格构建；`dev` 实时预览。`build` 按项目版本生成 major.minor.x 并提交到本地
 gh-pages；`deploy` 推送到 github 远端。现有节点说明保存在 `docs/nodes/`，机器参考保存在
`.agents/skills/use-omoo-nodes/references/node-catalog.json`。
