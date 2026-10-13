## Context

工具包测试负责构建和往返，节点单元测试负责正式节点的计算结果。项目已有隔离 bpy 环境和原生资产构建流程。

## Goals / Non-Goals

以节点名组织直接、可读的 pytest 单元测试，完整覆盖 Deform 分类。每个节点先覆盖有意义的正常输入和关键边界；全库所有参数组合不属于本次范围。

## Decisions

### 文件就是测试入口

`tests/nodes/<资产库>/<geometry|shader|compositor>/test_o_<节点名>.py` 内直接定义 `test_o_<节点名>`。多组输入用 pytest 参数化；不维护额外用例表。共享求值函数在 `evaluation.py`。

### 使用原生 pytest

`conftest.py` 在宿主中将每个节点文件收集为各配置目标的一项测试，在目标 bpy Python 中执行该文件的普通 pytest。目标环境仅补充现有测试依赖 pytest，源码通过 `select_sources()` 按目标选择。各节点独立进程，测试前清空 Blender 数据，调用正式源码的 `ASSET.create_group()` 创建被测节点及依赖。失败显示原生 pytest 日志，每节点执行超时为 120 秒。

几何字段通过 depsgraph 和属性读取，图像节点通过 CPU 渲染或合成读取线性 EXR。期望由数学计算、几何约束或明确约定给出，整数精确比较，浮点声明容差。O Stroke 按原有设计验证 Color Alpha=0.5 时完全覆盖处的 Alpha=0.25。

### 覆盖与运行

当前 14 个节点的具体断言与待补内容见 `docs/develop.md`。Deform 目录的资产必须存在同名测试文件。使用 `uv run pytest tests` 运行全部，使用 `--node-target b45` 选择目标，以文件路径或 `-k o_blend` 选择节点。

## Risks / Trade-offs

- 每节点一个进程增加少量启动耗时，获得直接的失败定位和原生状态隔离；目标环境与源码按会话复用。
- 图像数值受求值设置影响，测试固定 CPU、线性数据和输入尺寸。
- 单元测试只说明已断言的行为，覆盖范围在开发文档中明确列出。
