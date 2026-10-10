## ADDED Requirements

### Requirement: Unified native Python API

系统 SHALL 提供沿用 nodebpy 节点类、Socket 运算、`>>` 连线与 `_build_group` 写法的 Python 构建 API，不依赖 nodebpy 运行时。核心语法兼容 Python 3.11，能够在 bpy 4.5 与 5.2 中创建原生 Geometry、Shader 和 Compositor 节点树。节点能力以当前目标为准。

#### Scenario: Construct in Blender 4.5
- **WHEN** 在仅安装对应 bpy 和 nodes 的 b45 环境构建受支持源码
- **THEN** 直接创建并保存 4.5 节点树，不启动 5.2 后端，不导入 nodebpy 或 5.2 独有 Blender 类型

#### Scenario: Unsupported target capability
- **WHEN** 源码请求目标不存在的节点、属性或 Socket
- **THEN** 报告具体源码和节点问题并停止，不静默跳过或替换功能

### Requirement: Faithful canonical export

系统 SHALL 导出可执行、可读的 Python，明确保存节点、接口、有效属性、默认值、连线顺序、依赖、资源与 Asset 元数据。特殊结构 SHALL 显式读写；无法表达的数据 SHALL 阻断回写。

#### Scenario: Complex asset roundtrip
- **WHEN** 同版本导出并重建含 Zone、动态接口、嵌套组、打包图像和材质的受支持资产
- **THEN** 保存重开后的语义结构、资源内容、接口与依赖归属保持一致，multi-input 顺序和 Zone 配对不变

#### Scenario: Unknown effective data
- **WHEN** 导出发现尚未支持的有效属性、动态集合或资源引用
- **THEN** 错误标明资产、节点和数据项，正式源码不被该次不完整导出覆盖

### Requirement: Stable repeated roundtrip

系统 SHALL 从首次规范化导出后保持同版本源码与语义结构稳定，不因再次 dev/sync 增加、删除或自动补偿节点。人工新增的未连接节点 SHALL 保留。

#### Scenario: Three unchanged cycles
- **WHEN** 在 b45 或 b52 内对已规范化的资产连续执行三轮 dev 和 dev -s，期间不编辑
- **THEN** 每轮 Python 内容一致，保存重开后的节点、连线、接口和有效属性一致，资源与 Asset 元数据不丢失

### Requirement: Complete target implementations

系统 SHALL 以低版本 `.py` 为默认共享实现，优先选择已有 `.b52.py` 完整替代；专用文件的 `DISABLED = True` SHALL 表示该目标停用，不回退基础。系统 SHALL 不把新版本 `.blend` 转存旧版本充当兼容实现。

#### Scenario: Equivalent native interfaces
- **WHEN** 4.5 与 5.2 的节点差异可在工具内部准确对应
- **THEN** 使用一份共享源码，工具在对应目标处理原生差异，不为 API 命名差异创建资产副本

#### Scenario: Disabled asset referenced by another asset
- **WHEN** b52 专用文件声明停用，但另一个 b52 资产仍引用它
- **THEN** 报告引用者和停用资产，不回退加载基础实现或生成缺失引用的产物

### Requirement: Shared edits remain shared

系统 SHALL 不以编辑版本单独决定是否拆分源码。原本共享的节点在高版本修改后，候选源码 SHALL 在所有仍使用该共享实现的配置目标内进行原生构建和结构保真验证；通过后覆盖共享 `.py`。失败 SHALL 保留源码并报告问题，不自动创建专用副本。结构验证 SHALL 不被表述为任意效果的语义等价证明。

#### Scenario: Compatible high-version edit
- **WHEN** b52 修改了共享资产，候选源码在 b45、b52 均通过构建、保存重开及读写保真检查
- **THEN** 回写共享 `.py`，不因编辑版本较高就额外产生 `.b52.py`

#### Scenario: Unchanged high-version asset
- **WHEN** 编辑库的有效内容与当前源码在 b52 构建出的内容相同
- **THEN** 不改写原共享文件，也不新增专用文件，不依赖历史基线文件

#### Scenario: Incompatible shared edit
- **WHEN** 候选源码在仍继承共享实现的某个目标不支持或读写丢失数据
- **THEN** 说明具体目标与问题并停止回写，操作者可调整共享实现或明确建立专用文件

### Requirement: Automatic layout

系统 SHALL 在 dev/build 中自动布局。源码 SHALL 不记录节点位置、布局快照或布局开关；导出 SHALL 消除自动布局引入的 Frame、连通 Reroute 和重复 Group Input。

#### Scenario: Editing layout only
- **WHEN** 人工仅移动节点或改变自动布局
- **THEN** dev -s 不因此改变源码中的节点逻辑
