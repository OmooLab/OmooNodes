独立安装与许可的剩余事项由 `unified-native-nodes` 接续；已完成记录保留。

## 1. 验证迁移与发布前置能力

- [x] 1.1 在临时副本中标记 AnyImage 公开根，验证 nodebpy dump/build 可处理未标记 Asset 的源，保留原文件摘要
- [x] 1.2 对 Depth Cutout 验证完整 nodebpy 往返、水平布局、目标保存与结构逻辑，不以此前直接排列试验替代转换验证
- [x] 1.3 用固定 bpy 5.2 的官方 listing 模块生成真实远程库，检查 schema、metadata、资产数量与 SHA-256，确认无自定义预览时的合法结果
- [x] 1.4 完成 O_Essentials/O_Extra 的跨版本结构、元数据、资源、双向覆盖与构建失败恢复验收；保留既有 Mix 行为诊断及 Granules 延期，不恢复效果验证

## 2. 在 OmooNodes 维护通用工具

- [x] 2.1 在 tools/nodes/ 明确通用工具边界，保留 nodes 入口与代码来源，独立发行及许可设置留待后续
- [x] 2.2 提取源码选择、组归属、布局和逻辑验证，完成调用项目配置发现；移除安装目录推断项目的代码
- [x] 2.3 把 nodebpy 后端也纳入 uv 隔离调度，验证 Python 3.11 消费者、3.13 后端和独立 b45/b52 环境互不污染
- [x] 2.4 实现 dev 与 dev --sync 的简洁调用，验证依赖闭包、完整编辑库、公开根、双向覆盖和程序化回写

## 3. 正式产物与命令

- [x] 3.1 接入 dump 全部 Asset 根及依赖，验证首次导入统一无版本后缀、保存版本来源记录、转换往返、无 Asset 诊断与共享辅助组分类
- [x] 3.2 实现 build 的统一节点库产物，默认 local、--remote 切换、--self-contained 本地化依赖以及依赖库自动构建
- [x] 3.3 将通用清理和远程生成验证迁入独立工具，删除 blend overlay 执行路径及旧入口
- [x] 3.4 验证 build 的分目标目录、全部成功后提交及失败恢复

## 4. OmooNodes 接入

- [x] 4.1 配置后端与 b45/b52 环境，CI 显式构建 b45 local 与 b52 remote，删除旧发布入口
- [x] 4.2 合并 scripts/ 保留的结构处理至 tools/nodes/，删除旧入口、释义生成和效果验证，保留现有文档；不增加 docs nodes
- [x] 4.3 更新 CI、AGENTS.md 与开发文档，验证 build 的完整双版本目录、项目发布流程的压缩包及上传前验收

## 5. AnyImage 临时迁移验证

- [x] 5.1 在临时目录将 10 个公开组与资源导入原生模块，验证配置发现与完整来源模块，不改 AnyImage 工作区
- [x] 5.2 记录 AnyImage 组名、Socket 与 identifier 对照结果；按用户决定暂缓 Shader identifier 修复，不阻塞 OmooNodes

## 验证记录

- 全量测试通过；当前范围为 O_Essentials/O_Extra 共 92 个资产，b52 完整导出覆盖与重建一致，远程库原生 listing 与摘要通过。
- b52 后端读取 b45 文件时迁移节点，O Stroke、O Mix Color 及其依赖的往返结构存在差异。
- 目标列表决定支持范围，最低目标为默认 dev 与通用基础版本；单版本工作区可自动识别，旧多版本工作区须显式选目标。
- Python 3.11 控制进程可调度独立 3.13 SDK 与 b52 环境；清除继承的 PYTHONHOME/PYTHONPATH，worker 使用隔离 Blender 用户目录。
- AnyImage 10 个公开组在临时目录完成 SDK 导出重建，Depth Cutout 逻辑一致；原工作区未改。
- AnyImage 的 O Image Layer、O Shadeless 逻辑一致，但 Socket identifier 重排。问题已记录；按用户决定，本次不继续处理 AnyImage，正式接入时另行验收。
- 1.4 覆盖真实 bpy 往返、元数据、新增与删除 Asset、共享图片和双向覆盖测试。
- 图像签名覆盖 packed 数据、colorspace、alpha mode；Asset 签名覆盖作者、描述、标签、catalog、接口标识和适用的组属性。
- dev 完整覆盖开发库，dev -s 完整导出并覆盖 Python 和资源；通用实现回写通用文件，既有专用实现按来源回写。
- 项目环境为 Python 3.11、bpy 4.5.14，nodebpy 仅在独立后端安装；双版本开发库实跑成功。4.5 Compositor 旧版存储通过原生临时写入释放，退出无内存泄漏提示，输入文件字节保持不变。
