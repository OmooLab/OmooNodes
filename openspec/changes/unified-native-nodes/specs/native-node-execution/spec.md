## ADDED Requirements

### Requirement: Standalone tool package

系统 SHALL 将原生构建/导出核心及现有 CLI 放入 `src/nodes_tool/`，形成一个独立可安装的工具包。命令 SHALL 保持为 `nodes`，Python API SHALL 使用 `nodes_tool`。安装产物和运行依赖 SHALL 不包含 OmooNodes 资产、文档工具或专用业务规则，不保留旧 tools.nodes 转发。

#### Scenario: Installed use outside this repository
- **WHEN** 在独立环境安装工具，并从含自身 `nodes/` 和 `tool.nodes` 配置的外部项目执行命令
- **THEN** 使用该项目的配置、源码与输出位置，不读取 OmooNodes 工作区、不依赖源码仓库路径、不与项目 `nodes` Python 包冲突

#### Scenario: Lightweight command startup
- **WHEN** 在未加载 bpy 的控制环境运行 `nodes --help`
- **THEN** 正常展示已有三个命令，不导入 Blender 或准备目标环境

#### Scenario: One core for API and CLI
- **WHEN** 项目通过 Python API 或 CLI 构建同一份节点源码
- **THEN** 二者调用同一原生核心，不需要另装 nodebpy，也不使用不同的中间图格式

### Requirement: Target-local execution

系统 SHALL 用所选目标的 bpy 完成构建、导出、保存和校验，隔离 Blender 用户目录。源码和运行核心由同一 nodes 工具提供；运行时 SHALL 不依赖 nodebpy 或独立 builder 环境。

#### Scenario: Build a b45 development library
- **WHEN** 执行 `nodes dev nodes/O_Extra --target b45 -o workspaces`
- **THEN** O_Essentials 与 O_Extra 按依赖顺序在 4.5 中构建、保存、重开校验并输出完整开发库，全程不在 5.2 中载入节点

### Requirement: Explicit import version

`dump` SHALL 支持 `--target` 并默认最低配置目标；sync SHALL 使用明确或唯一工作区目标。在导出输入及依赖前 SHALL 检查保存主次版本与目标一致，补丁版本差异允许。

#### Scenario: Input saved by another major-minor version
- **WHEN** 用 b45 同步实际由 5.2 保存的开发库，或 dump 的输入依赖保存版本不匹配
- **THEN** 明确报告实际版本、目标和文件，停止导出及回写，不自动升级或降级节点结构

### Requirement: Simple overwrite and library output

系统 SHALL 保持 `dev`、`dev -s`、`build`、`dump` 的单一入口、直接覆盖方向和简短进度，使用现有资产库目录与依赖格式。build SHALL 保留本地、独立本地和 b52 remote 发布行为。

#### Scenario: Human and AI alternate edits
- **WHEN** 操作者运行 dev，随后在 Blender 编辑并运行 dev -s
- **THEN** dev 覆盖对应开发库，dev -s 覆盖对应 Python 和资源，不增加基线、冲突合并或双向自动同步

#### Scenario: Export worker fails
- **WHEN** 任何文件的导出或必要校验失败
- **THEN** 停止后续流程，不把尚未完成的一批导出写入正式源码；错误文件不显示成功标记

#### Scenario: Small script-generated library
- **WHEN** 独立项目只有一个简单节点库和最低配置
- **THEN** 同一套 nodes 能在目标内构建标准 library，消费者可按原节点组名载入，无需 OmooNodes 专用模块或额外后端

### Requirement: Verified migration and removal

系统 SHALL 在正式切换前通过两个目标的现有资产验证及简单消费者验证，保留采用代码的来源许可。切换后 SHALL 删除 nodebpy 运行依赖、配置、旧导入和兼容补丁。

#### Scenario: Correctness of affected assets
- **WHEN** 迁移 O Mix Color、O Stroke 及其依赖资产
- **THEN** 分目标验证非平凡 Alpha 混合和非零位移效果，连续同版本往返稳定；当前已经损坏的源码或图结构不作为唯一正确性依据

#### Scenario: Production switch
- **WHEN** 完成迁移并运行全部相关测试
- **THEN** 项目实际执行路径只使用统一 nodes，本地与 CI 配置一致，文档描述与实现一致，旧 nodebpy 后端不保留为回退层
