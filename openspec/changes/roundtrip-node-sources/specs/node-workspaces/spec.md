## ADDED Requirements

### Requirement: 本地与 CI 共享环境和版本配置

系统 SHALL 将 nodebpy 与 bpy 作为项目 dev 依赖锁定，并从项目环境读取转换后端。
每个目标的 Python 与 bpy 完整版本 SHALL 集中定义在 pyproject.toml 的 tool.nodes.targets。
系统 SHALL 用 uv 为所有目标准备独立环境，项目转换后端与目标环境分开管理。
所有目标 SHALL 用自己的 bpy 做检查、保存、重载与发布清理，worker MUST 在处理资产前检查实际版本。

#### Scenario: 目标环境版本错误
- **WHEN** 目标环境实际 bpy 不符合项目所定完整版本
- **THEN** 构建失败且不覆盖编辑库

#### Scenario: 转换后端升级
- **WHEN** 项目 nodebpy/bpy 后端升级到 5.3 而仍发布 b45、b52
- **THEN** 两个目标仍分别使用所定 4.5 与 5.2 环境检查和保存，不跟随后端升级

### Requirement: CI 从正式脚本构建发布资产

release workflow SHALL 复用本地 uv 环境调度，从 nodes 构建完整工作区，
通过既有资产构建工具生成发布库，再按 b45、b52 打包。CI 与本地 SHALL 复用同一发布入口，
工作基线 MUST 不进入发布产物。

#### Scenario: 标签触发资产发布
- **WHEN** v* 标签触发 release
- **THEN** 从 nodes 生成两个版本的资产压缩包，任何构建失败均阻止发布

### Requirement: 分版本临时源码包含完整依赖

系统 SHALL 从 nodes 的正式模块的文件名规则选择目标实现，组织为 b45、b52 独立临时源码目录，将选中的 .b52.py 在临时目录改为无后缀逻辑模块名，再调用 nodebpy build。临时目录 MUST 包含所有目标资产及完整依赖，正确组织原生导入，不同时加载同名组的两份版本实现。b45 选择无后缀模块，b52 优先选择 .b52.py，缺少专用文件时选择并验证通用模块。正式存储的共享模块 SHALL 仅保存一次，允许复制到两个临时目录。

#### Scenario: 共享模块构建两版本
- **WHEN** 节点组适配 b45、b52
- **THEN** 两个临时构建目录均包含该完整模块，而 nodes 只保留一份

#### Scenario: 构建同名版本
- **WHEN** 同一组存在不同 b45、b52 实现
- **THEN** 各临时目录只包含其目标实现，依赖导入指向同一目标的正确组

#### Scenario: 依赖缺失
- **WHEN** 所选目标缺少依赖、接口不匹配或出现递归依赖
- **THEN** 报告完整依赖路径，构建失败，不生成缺失引用的编辑库

### Requirement: 两个编辑工作区都是完整库

系统 SHALL 生成 workspaces/b45、workspaces/b52 的完整编辑库，保留资产库名、文件归属、分类与同版本跨库相对依赖。每个库 MUST 包含该目标的全部资产和完整依赖，不引用另一版本、旧源库或发布目录。每次 nodebpy build SHALL 使用干净独立 Blender 进程，避免同名缓存污染。

#### Scenario: 编辑 b52 内部依赖
- **WHEN** 人打开 b52 资产并进入其 O Essentials 依赖
- **THEN** 能编辑完整正确版本的节点内容，不只有局部更新组

### Requirement: 跨库链接保留唯一编辑归属

系统 SHALL 按依赖顺序准备目标版本资产库，构建后将跨库组引用恢复为指向同版本所属文件的相对 linked 引用。系统 MUST 不把 nodebpy 的 Python import 当作已恢复 Blender 文件链接。公共组 SHALL 仅在所属文件可编辑，引用库不生成第二份正式来源；依赖已有未同步逻辑时 MUST 拒绝覆盖。

#### Scenario: 构建 Extra 自动准备 Essentials
- **WHEN** 执行 nodes build nodes/O_Extra -o workspaces
- **THEN** 自动准备同版本 Essentials 并保留 Extra 对它的相对链接，无需分别指定依赖路径

#### Scenario: 修改公共组
- **WHEN** 用户需要修改 Extra 引用的 Essentials 公共组
- **THEN** 在 Essentials 所属文件修改，Extra 保留 linked 引用

### Requirement: AnyImage 是 build 后处理

系统 SHALL 在 nodebpy build 后对 Blender 内存中的节点树执行 AnyImage 整体整理，再保存完整编辑库。整理 MUST 覆盖计算分块、局部 Group Input、隐藏未用 Socket、字段放置、数学折叠、Frame 与 Reroute，并作为最后的布局步骤。所需代码、公共函数与尺寸数据 SHALL 经来源和许可检查纳入项目，不依赖外部项目路径。系统 MUST 验证布局前后及保存重载后逻辑一致。

#### Scenario: 复杂组人工维护
- **WHEN** 构建类似 Depth Cutout 的复杂组
- **THEN** 得到分块、分散输入与有组织的连线，接口、逻辑及求值保持一致

#### Scenario: 整理尚未支持目标树
- **WHEN** 树类型或 Zone 无法可靠整理
- **THEN** 明确失败，不静默输出未经完整整理的编辑库

### Requirement: b45 生成路径必须实际验证

系统 SHALL 区分转换后端运行版本与目标编辑库版本，不假设存在 nodebpy 450.x 或改 executable 就能直接构建 b45。采用 5.2 构建、4.5 打开检查并保存的路径时，系统 MUST 校验有效属性、接口、依赖、逻辑、保存重载和必要行为，读取损失必须阻止交付。最终 b45 文件 SHALL 由实际 4.5 保存。

#### Scenario: 文件可打开但配置丢失
- **WHEN** 4.5 成功读取 5.2 构建的候选却丢失有效字段或改变行为
- **THEN** 报告验证失败，不将损失后的图视为正确的 b45 实现

### Requirement: 基线与构建替换保护人工修改

系统 SHALL 保存实际目标、执行 Blender 与 nodebpy 版本、源摘要、稳定组映射和逻辑基线；临时构建通过保存重载检查后才替换目标。有未同步逻辑修改且未显式 force 时 MUST 拒绝覆盖。

#### Scenario: 构建失败或有未同步修改
- **WHEN** 创建、整理、目标验证或重载失败，或工作区含未同步逻辑且未指定 force
- **THEN** 原编辑库保持完整，临时结果不覆盖目标

### Requirement: 发布继续使用完整目标库

build_assets.py SHALL 接收已验证的完整工作区并检查其目标与执行 Blender 一致，沿用清理、本地依赖、独立本地化与远程 listing、metadata、缩略图和 SHA-256 检查。脚本 MUST 仅依赖 bpy 与标准库。旧 blend overlay 合并路径 MUST 被前置版本选择取代。

#### Scenario: b45 本地与 b52 远程发布
- **WHEN** 分别用对应 Blender 发布已验证的完整目标工作区
- **THEN** 保留现有模式约束与校验；输入目标不一致时在修改产物前失败

