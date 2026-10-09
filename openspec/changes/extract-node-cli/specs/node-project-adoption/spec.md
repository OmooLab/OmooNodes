## ADDED Requirements

### Requirement: OmooNodes CI 按构建验收打包接入

OmooNodes SHALL 用 nodes build 构建正式双版本库，由项目发布流程压缩产物，
在上传前运行结构与依赖验收。scripts/ 保留功能 SHALL 合并到 tools/nodes/ 并删除旧入口，节点释义生成与效果验证 SHALL 移除；本次 MUST 不新增 docs nodes。
通用逻辑和旧 blend overlay 路径 SHALL 在接入验证后删除。

#### Scenario: 标签发布
- **WHEN** v* 标签触发发布
- **THEN** 从 nodes 构建完整 b45 本地库与 b52 远程库，由项目发布流程压缩，验收失败则不上传

### Requirement: AnyImage 先在临时目录验证迁移

本次 SHALL 在临时目录验证 AnyImage 现有产物的 10 个公开组到 nodebpy 原生来源的迁移、完整往返、布局、公开名称与接口，MUST 不修改 AnyImage 工作区。
Shader identifier 差异 SHALL 按用户决定仅记录并暂缓处理，不阻塞 OmooNodes。实际接入 SHALL 随未来独立发行进行，通过插件引用接口验收后再替换发布输入，保留插件 pack 与运行时，删除已替换旧定义。

#### Scenario: Depth Cutout 往返失败
- **WHEN** 复杂组无法通过 nodebpy 导出、重建或目标功能验证
- **THEN** 阻止该项目切换，不删除原来源，不靠读取成功宣布迁移完成

### Requirement: 原往返验收与延期事项保持有效

工具 MUST 完成当前两个库的结构、资源、元数据、跨版本保存、冲突与失败恢复验收；求值效果验证不在本次范围，既有 Mix 行为诊断 SHALL 保留。
Granules SHALL 保持缺失依赖诊断并暂缓迁移；自定义图标恢复 SHALL 留待单独变更。

#### Scenario: 工具可复用但同步仍未完成
- **WHEN** 新 CLI 已实现但双工作区冲突或跨版本行为校验尚未通过
- **THEN** 相应任务仍未完成，不以新提案或打包成功代替往返验收
