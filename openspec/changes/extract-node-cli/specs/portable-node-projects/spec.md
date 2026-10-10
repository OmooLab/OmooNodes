## ADDED Requirements

### Requirement: 独立工具读取调用项目

系统 SHALL 先在 OmooNodes 的 tools/nodes/ 维护通用 CLI 和 nodes 命令，支持 Python 3.11 起的控制进程，保留未来提取独立包的边界。
节点来源 SHALL 保留在项目 nodes 目录。CLI MUST 从调用项目的 pyproject.toml
读取配置，不使用安装包路径推断项目，也不复制通用实现到消费者仓库。

#### Scenario: 在临时消费者调用工具
- **WHEN** 临时 Python 3.11 消费者使用 AnyImage 来源副本执行 nodes dev
- **THEN** 使用消费者配置和源码副本，OmooNodes 的配置与文件不参与处理

### Requirement: 构建后端与目标环境分离

系统 SHALL 用 uv 准备隔离 nodebpy/bpy 后端和所有声明的目标 Python/bpy 环境。
后端 SHALL 负责 dump/build，各目标 SHALL 负责检查、保存、重载与正式清理。
实际版本 MUST 在处理前检查；只准备声明的目标，主项目 MUST 不因后端版本被迫升级 Python。
省略后端配置时 SHALL 使用 Python 3.13、nodebpy 520.34.1、bpy 5.2.2；配置表 MAY 仅覆盖其中部分字段。
目标 MUST 在非空的 `tool.nodes.targets` 列表中声明。最低目标 SHALL 作为默认 dev 目标和通用基础版本。
精确 bpy 版本 MAY 通过 `tool.nodes.versions` 表覆盖已声明目标；省略时使用工具内置已验证版本，不联网查询。
系统 SHALL 为 b45 匹配 Python 3.11，为 b52 匹配 Python 3.13；未知目标、版本不匹配或旧嵌套配置 MUST 报错。
系统 MUST 不补入未声明目标。

#### Scenario: 省略后端配置
- **WHEN** 项目只声明目标环境，没有 `tool.nodes.backend`
- **THEN** 使用默认独立后端，目标版本和项目 Python 环境保持各自配置

#### Scenario: 后端升级而保留 b52
- **WHEN** 后端升级到 530.x，项目仍声明 b45/b52
- **THEN** 目标检查和保存继续使用所定 4.5/5.2，不改用后端 bpy

### Requirement: 原生模块与精确版本选择

系统 SHALL 保存 nodebpy 原生模块和现有共享辅助组划分，按无后缀及精确版本后缀选择完整实现。
专用实现优先，通用实现只在目标实际验证后交付。公开组 SHALL 使用原生 ASSET 定义，collection.json SHALL 描述文件归属与依赖，正式产物
SHALL 统一为节点库，local/remote 分发由 build 的 --remote 决定，省略时为 local；MUST 不维护等价手写源码、DSL 或版本增量补丁。

#### Scenario: 同名不同实现
- **WHEN** node_a.py 与 node_a.b52.py 并存
- **THEN** b45 选前者，b52 选后者，并在各自临时目录使用相同逻辑模块名解析依赖

### Requirement: 普通节点组可以成为公开根

dump SHALL 导入全部 Asset 根及其依赖，不提供名称筛选。历史普通组迁移 SHALL 先在迁移副本标记公开根，再调用 dump。
dev SHALL 以公开根建立基线并允许人工贡献，公开根使用 Asset 标记，
保留公开组、接口和完整依赖。原文件 MUST 不因导出而改变。

#### Scenario: 迁移 AnyImage 普通组
- **WHEN** 在迁移副本标记 O Image Depth Cutout 等公开根后 dump
- **THEN** 得到可重建的原生模块，辅助组保持辅助身份，原文件摘要不变
