## ADDED Requirements

### Requirement: 两个 CLI 编排原生转换流程

系统 SHALL 仅提供 nodes build SOURCE -o WORKSPACE 和 nodes sync SOURCE -s WORKSPACE，自动准备目标 bpy 环境，识别版本及依赖。build SHALL 组织临时源码并调用 nodebpy build、AnyImage 整理、跨库链接恢复和目标验证；sync SHALL 临时 dump、报告变化、验证后合并到 nodes。差异和必要检查 MUST 内置，不提供独立 diff、check 命令。CLI MUST 不维护另一套节点转换器。

#### Scenario: 双版本同步
- **WHEN** sync SOURCE -s workspaces 发现 b45 和 b52 工作区
- **THEN** 分别生成临时导出目录，再一次性比较、验证和合并正式来源

#### Scenario: 单版本同步
- **WHEN** sync SOURCE -s WORKSPACE 只发现 b52 工作区
- **THEN** 只提取该工作区，其他版本来源保持原内容，除非按共享实现更新规则或显式 apply-to 验证后更新

### Requirement: dump 使用支持读取文件的后端

系统 SHALL 调用 nodebpy dump 输出分版本临时模块，不直接覆盖 nodes。转换后端 MUST 支持读取工作文件；b45 编辑库可以由经过验证的 5.2 后端读取并导出，不强制 dump 运行于 4.5。导出 MUST 使用临时副本消除空间信息，不修改人的编辑文件。

#### Scenario: b45 人工修改后导出
- **WHEN** 用户在 4.5 保存编辑库
- **THEN** 已验证的后端将其导出到 b45 临时目录，版本归属仍为 b45，不由后端版本决定

### Requirement: 回写依据资产库和文件归属

系统 SHALL 从每个组的所属文件提取本地实现，过滤引用库的 linked 副本，按稳定归属回写对应 nodes 资产库。sync 指定库时 SHALL 同时检查其依赖库的变化，存在依赖修改时一并按归属验证和同步。所有涉及库 MUST 使用一致基线并原子提交，不允许从引用副本覆盖公共来源。

#### Scenario: 同步 Extra 及修改过的 Essentials
- **WHEN** 执行 nodes sync nodes/O_Extra -s workspaces 且两个所属文件均有修改
- **THEN** Extra 组回写 nodes/O_Extra，公共组从 Essentials 所属文件提取并回写 nodes/O_Essentials，全部验证后一起提交

#### Scenario: 引用副本无法确认归属
- **WHEN** 用户本地化 linked 公共组而产生与所属组冲突的副本
- **THEN** 同步报告归属冲突并保留正式来源，不自动覆盖公共组

### Requirement: 差异基于基线和准确逻辑

系统 SHALL 按稳定组 ID 对齐临时导出与 manifest，比较准确规范化逻辑及必要元数据。未修改组 MUST 不重写。模块位置变化、布局变化、代码格式变化或已验证的版本默认差异 MUST 不独立造成逻辑修改。代码文本与 nodebpy 自带 parity MUST 不作为唯一等价依据。

#### Scenario: 小幅数值变化
- **WHEN** 人修改对应类型精度内可识别的默认值
- **THEN** diff 报告变化，不用粗略舍入隐藏修改

#### Scenario: 无修改往返
- **WHEN** 新构建的编辑库立即 sync
- **THEN** 不改变源模块或版本归属

### Requirement: 合并共享实现及独立版本

系统 SHALL 将逻辑及必要元数据相同的完整实现合并为一份无后缀模块，不同实现分别保存为无后缀与 .b52.py 完整模块。共享实现修改 SHALL 在原适配范围验证，全部通过则更新一份，仅确定部分适配则拆分并保留其他目标旧实现。已有不同版本实现 MUST 不因候选在另一目标可构建就自动覆盖。apply-to SHALL 显式统一所选目标并经完整验证。

#### Scenario: 共享修改仅适配 b52
- **WHEN** 原实现支持 b45、b52，候选在 b52 通过而确定不支持 b45
- **THEN** 旧完整模块保留为 node_a.py，新完整模块保存为 node_a.b52.py

#### Scenario: 不同版本变为一致
- **WHEN** 两份完整实现的规范化逻辑和必要元数据一致
- **THEN** 正式来源只保留无后缀模块，删除重复的 .b52.py

#### Scenario: 两工作区对共享组作不同修改
- **WHEN** b45、b52 都修改同一基线中的共享组而候选不同
- **THEN** 报告冲突并停止回写，待用户明确分版本保存或统一候选后验证，不静默选择一份覆盖

#### Scenario: 原有不同效果
- **WHEN** 修改已有独立 b52 实现，而候选也能在 b45 构建
- **THEN** 默认保留 b45 原实现，只有显式 apply-to 才统一更新

### Requirement: 精确版本由完整验证确定

系统 SHALL 验证目标 Blender 的节点类型、有效属性、枚举、Socket、动态集合、赋值回读、完整依赖、保存重载和必要行为，不以目标版本大小或文件能打开推断兼容。父组 SHALL 在目标中解析正确的依赖实现，新组 SHALL 声明实际确认通过的文件名版本归属。

#### Scenario: 属性或依赖限制
- **WHEN** 候选的有效属性、Socket 或依赖只被 b52 支持
- **THEN** 报告具体限制和依赖路径，候选保存为 .b52.py；缺少所需通用实现时报告未完成，不掩盖失败

### Requirement: 工具失败不能被解释为版本限制

后端不可用、崩溃、未知提取配置、静默字段损失、赋值截断、重载不一致或行为失败 MUST 阻止同步。系统 MUST 不依靠不存在的 450.x，不为完成回写而自动标记仅 b52。

#### Scenario: 4.5 验证不完整
- **WHEN** 4.5 崩溃或读取候选时有未解决的数据损失
- **THEN** 报告未完成验证，保留正式来源与基线

### Requirement: 冲突删除与依赖受到保护

源摘要与编辑基线不一致时系统 MUST 拒绝覆盖。缺失组 MUST 不自动删除；显式 delete SHALL 仅移除参与编辑版本的实现并检查剩余依赖；删除 b45 时将保留的 b52 完整实现存为 .b52.py，删除 b52 但仍保留无后缀模块时必须报告通用回退冲突。重复或不明稳定 ID、悬空组、未管理外部引用及接口变化破坏依赖 MUST 阻止同步。

#### Scenario: 旧工作区覆盖新来源
- **WHEN** 一个版本同步后，另一旧工作区再尝试同步
- **THEN** 报告源已变化并保留编辑文件，不覆盖新的正式来源

#### Scenario: 误删或破坏依赖
- **WHEN** 工作区缺少基线组而未显式删除，或候选接口破坏已有组
- **THEN** 同步失败并指出冲突，正式来源不变

### Requirement: 临时合并验证后提交完整结果

系统 SHALL 在临时正式来源中合并 nodebpy 导出模块与归属配置，重建受影响目标的完整库，全部通过后更新 nodes 和参与同步的基线。多文件失败 MUST 能恢复全部旧内容。bootstrap SHALL 对旧完整库执行相同 dump、依赖及版本验证，不静默跳过未支持组。

#### Scenario: 部分候选失败
- **WHEN** 多个组变化，其中一个不能正确往返
- **THEN** 全部正式模块与配置保持原样，基线不推进

#### Scenario: 接口 identifier 变化
- **WHEN** 导出重建导致接口 identifier 改变
- **THEN** 报告映射并验证嵌套引用，不根据显示名相同宣称旧用户工程兼容

