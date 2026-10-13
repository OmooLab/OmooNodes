## Why

资产能构建不代表节点输出正确。需要以节点为单位验证输入与输出，并让测试文件、运行命令和失败位置容易理解。

## What Changes

- 现有工具测试迁至 `tests/cli/`，节点单元测试放在 `tests/nodes/<资产库>/<树类型>/test_o_<节点名>.py`。
- 使用普通 pytest 函数和参数化直接验证正式节点；共覆盖 14 个节点，其中 Deform 类 9 个全部覆盖。
- 复用目标 bpy 环境与源码选择，直接创建被测节点及依赖，按节点隔离执行。
- O Stroke 保持原有平方 Alpha 设计，测试明确验证该行为。

## Capabilities

### New Capabilities

- `node-behavior-tests`：节点单元测试、原生目标执行及 Deform 覆盖检查。

### Modified Capabilities

无。

## Impact

修改测试目录、项目规范和开发文档。复用现有 pytest 与 bpy，不增加产品 CLI 命令或修改正式节点功能。
