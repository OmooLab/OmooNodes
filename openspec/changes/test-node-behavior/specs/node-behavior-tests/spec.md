## ADDED Requirements

### Requirement: 节点命名的单元测试

项目 SHALL 使用 `tests/cli/` 保存工具测试，在 `tests/nodes/<资产库>/<树类型>/test_o_<节点名>.py` 中以普通 pytest 函数验证节点输入与输出。

#### Scenario: 新增节点测试
- **WHEN** 添加节点测试文件
- **THEN** pytest 自动发现它，无需登记场景或实现分发函数

### Requirement: 真实求值和明确预期

节点测试 SHALL 使用目标版本正式源码在原生 bpy 中创建被测节点及依赖，读取实际几何、字段或像素输出，并对照独立计算或明确行为约定；每个节点 MUST 覆盖有效结果与关键边界。

#### Scenario: 描边透明度
- **WHEN** O Stroke 的 Color Alpha=0.5
- **THEN** 完全覆盖处输出 Alpha=0.25，保留平方透明度设计；Alpha=0 时描边透明

### Requirement: 目标执行和隔离

节点测试 SHALL 默认运行全部配置目标，支持 `--node-target` 和按节点文件筛选。目标环境和源码 MUST 会话内复用，各节点独立进程执行，每项测试清空数据并重新创建节点。

#### Scenario: 选择单个节点
- **WHEN** 执行 `uv run pytest tests/nodes/O_Essentials/geometry/test_o_blend.py --node-target b45`
- **THEN** 只在 b45 执行 O Blend 单元测试

#### Scenario: 求值失败或进程异常
- **WHEN** 原生 pytest 断言失败、退出异常或超过 120 秒
- **THEN** 对应节点和目标测试失败，保留日志，不计为通过

### Requirement: Deform 完整覆盖

Deform 分类 SHALL 全部具有节点单元测试，开发文档 SHALL 记录已测行为与待补范围，默认全量入口 MUST 包含节点测试。

#### Scenario: 分类新增资产
- **WHEN** Deform 目录有资产缺少同名测试文件
- **THEN** 目录覆盖检查失败并报告缺少的节点
