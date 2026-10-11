## Why

需要一个独立、简单的节点库工具，让任意项目用可读 Python 与 Blender 原生节点库双向转换，最低支持 Blender 4.5。现有 nodes CLI 已有适用的工作流，但固定 nodebpy / 5.2 后端的跨版本转存无法可靠往返。

新 nodes 将必要的构建、导出核心和已有 CLI 合为一个独立包。OmooNodes 是复杂消费者和验证样本，AnyImage、BioxelNodes 一类简单节点库同样适用；工具不包含这些项目的业务规则。

## What Changes

- **BREAKING**：移除运行时 nodebpy 依赖及固定 builder 环境。b45 使用 Python 3.11 / bpy 4.5，b52 使用 Python 3.13 / bpy 5.2；构建、导出、校验都在所选目标内执行。
- 改编 nodebpy 520.34.1 的构建器、节点包装和表达式导出器，保留其书写方式；布局、资产管理和 CLI 复用本工具实现。
- **BREAKING**：工具实现位于 `src/omoonodes/`，包名与 Python API 使用 `omoonodes`，命令为 `omoonodes`，独立打包安装。项目自己的 `nodes/` 仅保存资产源码，与工具包分开。
- **BREAKING**：正式源码使用 nodebpy 的节点类、Socket 运算和 `>>` 表达式，包名为 `omoonodes`。源码不记录节点位置和布局开关，dev/build 自动布局。
- 保留 `dev`、`dev -s`、`build`、`dump`、资产库目录、跨库依赖、`.py` / `.b52.py` 完整实现约定及当前简短输出。`dev` 和 `dev -s` 继续直接覆盖。
- 低版本 `.py` 默认共享；高版本兼容修改经跨目标验证后回写共享源码，确有差异才使用 `.b52.py`。版本停用用专用文件中的 `DISABLED = True` 表达，不因为在高版本编辑就自动复制一份源码。
- `dump` 增加与其他命令一致的 `--target`；省略时选项目最低目标。目标与输入保存版本不匹配时给出明确诊断，避免把跨版本迁移混进日常往返。
- 对现有资产一次性迁移和修复：按各目标原生语义保留行为，不把已累积的转换节点或丢失的连线当作正确基线。
- 完成同版本连续往返、真实 OmooNodes 资产及简单脚本库验证后，一次切换命令实现，删除旧后端和补丁。

## Capabilities

### New Capabilities

- `native-node-authoring`：Python 3.11 起的统一构建 API、原生结构导出和稳定往返。
- `native-node-execution`：按目标执行全部节点操作、直接覆盖、依赖与发布，以及迁移验收。

### Modified Capabilities

无。`openspec/specs/` 尚无已归档的对应规格；本提案在上述能力范围内替代 `roundtrip-node-sources`、`extract-node-cli` 中依赖 nodebpy 后端的设计，不重开它们已完成的 CLI 清理。

## Impact

- 主要涉及 `src/omoonodes/`、旧 `tools/nodes/` 的迁移、独立包元数据、消费者配置和相关测试；OmooNodes 的资产迁移、CI、开发文档及 AGENTS.md 单独作为接入工作。
- 本仓库先承载可独立安装的工具源码，安装产物不携带 OmooNodes 资产、文档或项目专用模块。新建远程仓库、上传 PyPI 和完整 IDE 节点类生成不在本次范围。
- 实施按“原型验证 → 核心覆盖 → 资产迁移 → 切换”推进；这是一次后端替换，不是增加几条版本判断。
- nodebpy 标注 GPL-3.0-or-later；采用其代码的 nodes 工具需保留来源、许可和修改说明，并调整对应发布元数据。提案不改变资产及其他独立部分的许可声明。
