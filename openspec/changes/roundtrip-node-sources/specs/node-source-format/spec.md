## ADDED Requirements

### Requirement: nodebpy 导出模块是正式存储格式

系统 SHALL 在 `nodes/<资产库>/` 保存 nodebpy 原生导出模块及其资产元数据、创建方法和依赖引用，不另设节点源码语言或要求项目专属注册列表。转换 MUST 程序化执行，不依赖 LLM。所有 `.blend`、临时源码和工作区基线 MUST 保持 Git 忽略。

#### Scenario: 人工编辑库回写
- **WHEN** 用户修改节点并完成 dump、验证与合并
- **THEN** 正式来源保存 nodebpy 生成的完整代码，没有另行维护的等价函数式源码

### Requirement: 模块划分沿用 nodebpy 依赖组织

系统 SHALL 沿用每个资产一个模块、专用辅助组内嵌、共享辅助组独立模块的规则，并保留节点树类型分类。资产嵌套 SHALL 使用模块导入，不重复保存被引用资产。组身份 MUST 由稳定 ID 和树类型确认，模块归类移动不能被误判为新组或删除。

#### Scenario: 一个资产引用另一个资产
- **WHEN** O Essentials 的资产 A 引用资产 B
- **THEN** A 导入 B 的实现，正式来源只有一份 B，构建得到实际完整引用

#### Scenario: 辅助组变为共享
- **WHEN** 原仅由 A 使用的辅助组又被 B 使用
- **THEN** 可移动到共享模块并调整导入，保留同一稳定组身份

### Requirement: 文件名决定通用与专用完整实现

系统 SHALL 以 `node_a.py` 保存尽可能通用、最低支持 b45 的完整实现，以 `node_a.b52.py` 保存仅用于 b52、不用于 b45 的完整实现。b45 SHALL 选择无后缀文件；b52 SHALL 优先选择 `.b52.py`，缺少专用文件时选择无后缀文件并验证。专用实现 MUST 独立完整，不与通用实现合并节点逻辑。系统 SHALL 用独立配置保存稳定组 ID、文件归属与依赖映射，不重复维护版本列表。最低支持 b45 MUST 不被当作未知未来版本已验证的保证。

#### Scenario: 两个版本相同
- **WHEN** 完整实现实际适配 4.5 与 5.2 且逻辑及必要元数据相同
- **THEN** 正式来源只保存 node_a.py，两个目标均选择它

#### Scenario: 同名不同版本
- **WHEN** 两个目标的同名组逻辑不同
- **THEN** 保存 node_a.py 和 node_a.b52.py，分别被 b45、b52 选中，每份包含全部逻辑

#### Scenario: b52 特有
- **WHEN** 只有 node_a.b52.py
- **THEN** 只进入 b52，不进入 b45，也不自动适配其他版本

#### Scenario: 通用实现不适配 b52
- **WHEN** 只有无后缀实现但 b52 兼容验证失败
- **THEN** 构建失败并要求解决兼容或补齐专用实现，不静默跳过

### Requirement: 比较保留精确逻辑并排除空间信息

系统 SHALL 使用内部规范化图比较接口顺序、有效值、配置、依赖、动态 item、Zone 配对、静音、精确连接端点及 Multi-input 顺序与重复次数。规范化字典 MUST 不作为正式节点存储。提取 SHALL 在临时副本中消除位置、大小、Frame、布局 Reroute、重复 Group Input 和编辑器状态，保留真实求值行为，不改人的编辑文件。

#### Scenario: 仅布局变化
- **WHEN** 用户移动节点、添加 Frame 或改变局部 Group Input 与 Reroute，但求值逻辑一致
- **THEN** 不重写正式模块或改变文件名版本归属

#### Scenario: 同名 Socket 与重复连接
- **WHEN** 接口或节点有同名 Socket，Multi-input 接收 A、B、A
- **THEN** 提取和重建精确区分 Socket 并保留连接顺序与三次输入

### Requirement: 不完整转换必须阻止写回

系统 SHALL 检查 nodebpy 对动态集合、Ramp、Curve、资源和有效属性的完整往返，使用经过验证的规则处理版本默认差异。未知配置、Driver、缺失资源、TODO 输出、宽松导出遗漏或求值不一致 MUST 报错，不能静默丢弃后保存来源。

#### Scenario: 特殊配置往返
- **WHEN** 用户修改支持的动态集合或 Zone
- **THEN** 完整保留 item 类型、顺序、配对和连接并通过实际重建

#### Scenario: 未支持配置
- **WHEN** 后端无法可靠导出求值配置或资源
- **THEN** 指出组和配置并阻止同步，正式来源不变
