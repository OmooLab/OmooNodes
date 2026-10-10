## Context

现有 tools/nodes 已有源码版本选择、双目标 bpy 环境、布局、逻辑比较和原子替换。
AnyImage 的 10 个公开组由手写 Python 构建，其主项目使用 Python 3.11；OmooNodes 项目环境同样使用 Python 3.11、bpy 4.5.14，nodebpy 仅安装在独立 Python 3.13 后端。
两项目需要共用工具，保留自己的资产、运行时、测试和发布职责。当前目标是 b45/b52，仅管理 O_Essentials 与 O_Extra。

## Goals / Non-Goals

**Goals**

- 在 OmooNodes 维护一份可提取的 `nodes` CLI，本地与 CI 使用相同版本和流程。
- 统一以节点库运作，服务插件引用、本地安装和远程分发，复用 nodebpy 原生源码。
- 主项目 Python、转换后端、目标 bpy 三者分离，允许后端升级而目标不变。
- 合并原 scripts 功能并接入 OmooNodes；在临时目录验证 AnyImage。

**Non-Goals**

- 新节点 DSL、LLM 回写、任意插件或回调框架。
- 发布上传、插件 ZIP 打包、自动生成效果释义、此次解决自定义图标恢复。
- 以源码可构建或文件可打开宣告跨版本功能兼容。

## Decisions

### 1. 先在 OmooNodes 维护，保留可提取边界

本次通用工具维护在 OmooNodes 的 tools/nodes/，命令入口为 nodes，控制层支持 Python 3.11 起。
稳定并验证第二个消费者后再提取为 node-cli 包，通用逻辑，包括转换编排、布局、版本选择、运行环境、
逻辑验证与正式节点库构建。保留 AnyImage 布局来源与 GPL 许可，独立包的许可设置留待发行时处理。

节点源码和文件归属仍在各自的 nodes/<集合>/。工具通过调用项目配置处理节点，不依赖 Omoo 硬编码。
scripts/ 的功能并入 tools/：结构处理进入 tools/nodes/；节点释义生成与效果验证移除。
删除旧脚本入口。worker 使用隔离的 Blender 用户目录，不加载或修改用户安装、偏好和扩展。未来独立发行时消费者固定工具版本。

### 2. 一个后端，若干独立目标

CLI 控制进程不导入 bpy。uv 准备隔离 nodebpy 后端和每个目标环境，进程之间用临时文件传递。
工具开发时可以安装 nodebpy，消费者无需在自己的主 Python 环境安装它。
后端负责 dump/build 与布局，各目标负责检查、保存、重载和发布清理。
缓存按 Python、nodebpy、bpy 精确配置区分，验证实际版本后才处理数据。
worker 只加载独立工具与当前环境，不能把消费项目的 site-packages 注入另一版本 Python。

项目声明节点来源和目标环境。独立后端默认 Python 3.13、nodebpy 520.34.1、bpy 5.2.2；
需要覆盖时才声明 `tool.nodes.backend`。正式构建始终输出节点库，分发方式独立于版本。

```toml
[tool.nodes]
source = "nodes"

targets = ["b45", "b52"]

# 可选覆盖
[tool.nodes.versions]
b45 = "4.5.14"
```

AnyImage 使用 local，可将所需节点库文件随插件分发并按组名引用，无需增加资产库安装界面。
只声明需要的目标，不自动补入其他目标；Python 按支持的 bpy 系列匹配：4.5 使用 3.11，5.2 使用 3.13。
用户直接修改 .py 后即可 build，不必经过 dev。

### 3. 只保留 dev、build、dump

所有命令提供 `-h/--help`。参数定义如下，不另提供 sync/export/pack/catalog 命令。

| 命令 | 输入 → 输出 |
| --- | --- |
| `nodes dev [SOURCE] [-o WORKSPACE | -s WORKSPACE] [--target TARGET]` | 默认准备完整开发节点库；--sync/-s 从开发库完整导出并覆盖源码 |
| `nodes build [SOURCE] [-o OUTPUT] [--target TARGET] [--remote] [--self-contained]` | 从源码构建正式节点库，默认本地，--remote 生成远程库 |
| `nodes dump INPUT -o SOURCE` | 现有节点库文件或目录 → 经验证的原生源码集合 |

SOURCE 省略时取 tool.nodes.source，未配置时为 nodes；可指定一个集合或来源根目录，自动处理依赖。
TARGET 为项目声明的精确目标标签，如 b45、b52；dev/build 省略时处理配置目标。
dump 首次导入统一使用无版本后缀 .py，原始 .blend 的保存版本只记录为来源信息。
无后缀源码遵循至少支持 b45 的约定，实际兼容性由后续 dev/build 验收，不由 dump 宣告。

**dev**

- `-o/--output WORKSPACE`：准备开发库的父目录，默认 workspaces。
- `-s/--sync WORKSPACE`：读取该目录的开发库，完整导出并覆盖来源；直接接收目录，不是布尔开关。
- 两者显式使用时互斥。省略两者相当于准备 workspaces。
- `--target TARGET`：准备或读取指定目标；省略时只准备最低目标；回写自动读取唯一工作区目标，多版本工作区须显式选择。
- dev 覆盖所选开发库，dev -s 覆盖对应 Python 和资源，由操作者决定覆盖方向。

**build**

- `-o/--output OUTPUT`：正式输出父目录，默认 dist，结果位于 OUTPUT/<目标>/<集合>/。
- `--target TARGET`：只构建指定目标；省略时构建全部配置目标。
- `--remote`：生成远程库；省略时生成本地库。
- `--self-contained`：本地库也嵌入外部依赖，便于独立分发；remote 已自动执行，两个参数一起传入也保持相同行为。
- remote 能力必须由目标支持。显式 remote 选中不支持的目标时，在处理产物前失败，不自动忽略该目标。
- 项目联系信息和固定版本写配置，不增加逐次传递的联系参数。必要检查全部内置。

**dump**

- INPUT：一个 .blend 文件或节点库目录，目录按文件归属导入并保持依赖关系。
- `-o/--output SOURCE`：写入的源码集合位置，必填；不覆盖已存在来源，已有来源变化走 dev --sync。
- 自动导入全部 Asset 节点组，递归保存所需辅助组，保留公开根与依赖归属，不提供名称筛选。
- 全部首次导入模块使用无版本后缀 .py，不自动生成 .b52.py。
- 原始文件保存版本只记录来源，不用于目标匹配或源码命名；dump 验证转换往返，目标兼容性由 dev/build 验收。
- 确需版本专用实现时，由开发者明确整理为 .b52.py 等版本文件。
- 没有 Asset 节点组时明确报错；历史普通组迁移前先在迁移副本中标记公开根，不修改原输入。

OmooNodes：

```bash
uv run nodes dev nodes/O_Essentials -o workspaces
uv run nodes dev nodes/O_Essentials -s workspaces
uv run nodes build -o dist
uv run nodes build nodes/O_Extra --target b45 -o dist
uv run nodes build nodes/O_Extra --target b52 --remote -o dist
```

AnyImage：

```bash
uv run nodes dev nodes/O_AnyImage -o workspaces
uv run nodes dev nodes/O_AnyImage -s workspaces
uv run nodes build nodes/O_AnyImage --target b45 -o dist
```

AnyImage 自己的插件打包程序从 dist/b45/O_AnyImage/ 取构建结果中的 O_AnyImage.blend，
放入插件既有 assets 路径；nodes 不打包插件代码。需要时显式 dump 完成首次源码迁移。

### 4. 原生源码与公开根

保持一根一模块、专用辅助组内嵌、共享辅助组 `_shared/` 的 nodebpy 划分。
无后缀 `.py` 适配项目最低配置目标，`.b52.py` 是精确 b52 完整实现，临时选择时改回无后缀名。
未来版本变体只在声明、实现并验证对应目标后启用，不按版本大小套用补丁。
来源使用 collection.json 描述集合文件和依赖归属，公开根使用模块原生 ASSET 定义。
SDK ASSET 声明与正式节点库的 Asset 标记保留。开发库包含全部公开组与依赖，便于查看、调试、修改；
dev 从源码生成并覆盖开发库。dev -s 完整导出 Asset 根、辅助组、元数据与 packed 图片，直接覆盖对应 Python 和资源，并移除已删除节点的生成源码。通用实现回写通用文件，已有 b52 专用实现回写专用文件。目标兼容性通过 dev/build 检查。

nodebpy dump 的 Asset 根要求与节点库约定一致。dump 导入全部 Asset 根及其依赖。
历史普通组迁移先在临时副本标记公开根，再调用 dump 并验证，原文件保持不变。不存在单独的普通 blend 正式产物分支；AnyImage 同样使用节点库，
插件直接引用其文件内的公开组，不要求终端用户安装资产浏览器目录。

### 5. 节点库的 local 与 remote 分发

local 保留 Asset 标记与 catalog，默认保留同版本库间相对引用并包含所需依赖集合。
--self-contained 将外部依赖嵌入所选库，本地分发时不再要求携带外部库。
AnyImage 的组及内部依赖都在同一个库文件中，插件直接引用该文件。
remote 自动本地化外部数据，生成原生 listing、metadata 和 SHA-256；目录适合上传 assets.omoolab.xyz/b52/<库>。
CLI 输出库目录；压缩包由项目发布流程或插件打包程序负责。

```text
dist/b45/O_Essentials/*.blend       本地库与 catalog
dist/b45/O_Extra/*.blend            相对引用同级 Essentials
dist/b52/O_Essentials/              独立资产、catalog、metadata、_v1 listing
dist/b52/O_Extra/                   已本地化外部依赖
```

复用 build_assets.py 的清理、模式约束及验证后移入独立工具，删除 blend overlay 路径。
b52 官方 bpy 包包含 `_bpy_internal.assets.remote_library.cli_listing_generator`，优先通过
固定目标环境调用原生模块；先验证真实生成和客户端兼容，再交付 remote 分发。
接口缺失、listing 不完整或摘要错误必须失败，不另写看起来相似的发布 JSON。
图标保持当前暂缓决定，不要求新增自定义图片恢复流程；无预览时验证原生格式允许的结果。
所有正式产物先在临时目录完成，成功后替换输出；build 使用独立临时目录，不覆盖人工编辑文件；所有选定目标通过后一起提交。

### 6. 项目脚本与验收归属

本次不增加 docs nodes，移除节点释义生成和效果验证。
删除 scripts/ 入口，结构提取归 tools/nodes/ 内部模块；移除节点释义生成与效果验证，不新增 catalog CLI 或 docs nodes，保留现有说明文档。
通用 CLI 负责结构、资源、版本、布局和保存重载检查。

本次不改 AnyImage 工作区，迁移验证全部在临时目录进行。未来接入时删除已替换的旧 nodes/groups、nodes/common 和旧节点工具；保留插件运行代码、
按名字加载的接口、属性名、现有功能测试和自己的 pack 命令。先验证全部 10 个公开组，
包括 Depth Cutout 的 nodebpy 往返与既有 Modifier 调用，再切换发布源。本次 AnyImage 的 Shader identifier 差异仅记录，按用户决定暂缓处理。

## Risks / Trade-offs

- 后端读旧文件可能插入转换节点：保留跨版本原始逻辑对比，未通过不得迁移。
- nodebpy 会重排部分接口 identifier：AnyImage 的 O Image Layer、O Shadeless 已确认存在差异，正式接入前验证引用处理。
- 原生 remote 模块是私有接口：固定 bpy 版本并做真实生成验收，升级必须重新验证。
- 历史普通组未标记 Asset：仅在临时副本提升指定根，验证后迁为节点库源码，校验插件加载接口。
- 输出清理可能影响资源和依赖：验证 packed 资源、相对路径与接口，失败不推进源码或产物。

## Migration Plan

先验证 Asset 根准备与 dump、原生 remote 生成，再在 OmooNodes 完成工具边界与新命令。
验证跨版本结构、元数据、资源、冲突与失败恢复后，合并保留功能并接入 CI。效果验证不在本轮范围，既有 Mix 求值行为诊断保留。
在临时目录验证 AnyImage 完整迁移；实际接入与独立发行留待工具稳定后，不修改其工作区。
roundtrip-node-sources 中的相关结构验收由本轮测试覆盖；未实施的求值、显式删除与旧命令选项不视为已完成。命令命名与职责以本设计及用户最新范围为准。

## Open Questions

未来独立发行的仓库地址与版本届时确定，暂名 node-cli。
