## Why

OmooNodes 和 AnyImage 都需要从 nodebpy 源码构建可编辑节点，并将节点库用于用户分发或插件内引用。将 CLI、布局和 bpy 环境调度按独立工具边界维护，可以复用已验证的流程，并让项目各自决定发布形式与目标版本。

## What Changes

- 先在 OmooNodes 的 tools/nodes/ 维护通用工具和 nodes 命令，按可提取的包边界组织；稳定并验证第二个消费者后再独立发行 node-cli，本次不创建独立仓库。
- CLI 控制层支持 Python 3.11 起；nodebpy 构建后端和各目标 bpy 都由 uv 准备隔离环境，AnyImage 无需为 nodebpy 升级主项目 Python。
- 只提供 dev、build、dump。dev 默认准备开发库，--sync/-s 接收工作区目录并验证回写；build 从源码构建 local/remote 正式节点库，默认 local，--remote 切换远程，--self-contained 支持独立本地库；dump 自动导入全部 Asset 根及依赖。
- nodes/ 保存 nodebpy 原生模块，版本文件规则不变；collection.json 记录文件与依赖，公开根由原生 ASSET 定义；目标配置声明 Python/bpy。
- 所有流程统一以节点库运作。AnyImage 同样构建单文件本地库，插件按原组名直接引用；OmooNodes CI 显式构建 b45 本地库与 b52 远程库。
- 移除独立 sync/export/pack/catalog 及普通 blend 正式产物分支。scripts/ 功能并入 tools/，保留的结构处理并入 tools/nodes/；移除节点释义生成、效果验证和旧入口，不增加 docs nodes。
- dump 首次导入统一保存为无版本后缀 .py；原始 .blend 保存版本只记录来源，不自动分类。兼容范围由 dev/build 验证，无需 --target 或 --names。历史普通组先在迁移副本标记 Asset 根，原文件不改；正式迁移完成后不维护两套定义。
- **BREAKING**：迁移完成后删除两项目的旧节点构建入口、复制的通用工具及旧 blend overlay 执行路径。AnyImage 本次仅在临时目录验证迁移能力，不改其工作区；实际接入随独立发行进行。

## Capabilities

### New Capabilities

- `portable-node-projects`：可提取的工具边界、项目配置、后端与目标环境隔离、原生节点源码和普通组根。
- `node-artifact-pipeline`：统一开发库、验证回写、本地/远程正式节点库目录构建。
- `node-project-adoption`：OmooNodes 正式产物与发布接入，AnyImage 节点源码迁移和消费接口验证。

### Modified Capabilities

## Impact

- 提取现有 tools/nodes、布局、运行环境、源码选择和校验；接入 build_assets.py 的通用清理与发布能力，保留来源和 GPL 许可。
- 更新 OmooNodes pyproject、CI 与项目验收调用链；AnyImage 作为第二个消费者在临时目录验证，保留自己的运行时和插件打包流程。
- 目标沿用 b45/b52。b52 listing 优先验证官方 bpy 包内的原生生成模块；私有接口按目标版本固定，不能未经验证宣称远程发布可用。
- 图标的提取和恢复继续暂缓；Granules 缺失依赖继续保留诊断。跨版本 Mix 和复杂组往返问题作为实施验收条件，不由工具提取自动解决。
