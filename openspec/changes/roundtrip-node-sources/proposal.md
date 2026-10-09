## Why

OmooNodes 需要让人和代码共同维护节点，并以 nodebpy 导出的代码作为唯一正式存储格式。共享节点只保存一份；b45、b52 的人工编辑库都包含该版本的全部资产与依赖。

## What Changes

- `nodes/` 保存 nodebpy 原生导出模块，不另设函数式源码或节点 DSL；版本由文件名决定：无后缀 `.py` 是最低支持 b45 的通用实现，`.b52.py` 是仅用于 b52 的完整实现；独立配置只记录归属和依赖。
- 构建时先从 `nodes/` 选择各目标的完整实现，组织成 b45、b52 分开的临时源码目录；b52 优先选专用文件，并在临时目录去掉版本后缀，再调用 nodebpy build。
- AnyImage 作为 build 后处理，在 Blender 中整理节点树并保存完整编辑库。
- 人工修改后，nodebpy dump 分别导出到 b45、b52 临时目录；比较基线、验证依赖与版本，合并后回写 `nodes/`。
- 共享实现以无后缀文件存一份，同名不同实现保存为 `.py` 与 `.b52.py`，b52 特有实现仅保存 `.b52.py`；不使用增量补丁。
- 仅提供 `nodes build nodes/O_Essentials -o workspaces` 和 `nodes sync nodes/O_Essentials -s workspaces` 两个命令；版本选择、临时目录与必要验证在命令内部完成，目标 bpy 环境自动准备。
- 构建自动按依赖顺序准备同版本资产库，恢复跨文件 linked 引用；公共组仅由所属资产库维护，sync 按归属从真实文件提取并回写，不能从引用副本覆盖来源。
- **BREAKING**：正式来源迁移到 `nodes/`，`workspaces/b45/`、`workspaces/b52/` 是完整编辑库；保留资产库名称、文件划分和相对依赖。
- `build_assets.py` 继续负责现有发布流程，输入改为已完成版本选择和验证的完整编辑库；临时源码、基线及 `.blend` 不进入 Git。

## Capabilities

### New Capabilities

- `node-source-format`：nodebpy 原生导出格式与文件名版本选择，共享实现不重复保存。
- `node-workspaces`：按版本组织临时源码、构建和整理完整编辑库，接入现有发布。
- `node-source-sync`：按版本临时导出、比较、验证与安全合并回写。

### Modified Capabilities

## Impact

- 新增 `nodes/` 正式存储和 `tools/nodes/` 薄工具，在 `pyproject.toml` 注册 `nodes`。
- 引入固定 nodebpy 后端及项目内 AnyImage 整理代码，保留来源和许可。
- Python 3.13 开发环境将 nodebpy/bpy 纳入 dev，版本由 uv.lock 锁定；各目标 Python/bpy 版本统一写入 pyproject.toml，本地与 CI 使用相同 worker 校验。
- release workflow 从 nodes 构建全部已迁移库，通过现有资产工具清理并按 b45、b52 打包；本地复用 tools.nodes.release 入口。
- b45 路径需实际验证：没有现成的 nodebpy 450.x。优先验证 5.2 构建后由 4.5 检查并保存，再由支持的 Blender 执行 dump；不能把读取成功视为兼容通过。
- 调整 `build_assets.py` 的完整库输入和相关测试，删除旧 overlay 合并路径，保持仅依赖 bpy 与标准库。
- 实施时按需更新 AGENTS.md、docs/develop.md 和 Git 忽略；提案阶段不迁移资产、不构建发布产物。

