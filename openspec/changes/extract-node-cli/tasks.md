## 1. 验证迁移与发布前置能力

- [x] 1.1 在临时副本中标记 AnyImage 公开根，验证 nodebpy dump/build 可处理未标记 Asset 的源，保留原文件摘要
- [x] 1.2 对 Depth Cutout 验证完整 nodebpy 往返、水平布局、目标保存与结构逻辑，不以此前直接排列试验替代转换验证
- [x] 1.3 用固定 bpy 5.2 的官方 listing 模块生成真实远程库，检查 schema、metadata、资产数量与 SHA-256，确认无自定义预览时的合法结果
- [x] 1.4 完成 O_Essentials/O_Extra 的跨版本结构、元数据、资源、同步冲突与失败恢复验收；保留既有 Mix 行为诊断及 Granules 延期，不恢复效果验证

## 2. 在 OmooNodes 维护通用工具

- [x] 2.1 在 tools/nodes/ 明确通用工具边界，保留 nodes 入口与代码来源，独立发行及许可设置留待后续
- [x] 2.2 提取源码选择、组归属、布局和逻辑验证，完成调用项目配置发现；移除安装目录推断项目的代码
- [x] 2.3 把 nodebpy 后端也纳入 uv 隔离调度，验证 Python 3.11 消费者、3.13 后端和独立 b45/b52 环境互不污染
- [x] 2.4 实现 dev 与 dev --sync 的简洁调用，验证依赖闭包、完整编辑库、公开根、未同步保护和程序化回写

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

- [x] 5.1 在临时目录将 10 个公开组与资源导入原生模块，验证配置发现与完整来源基线，不改 AnyImage 工作区
- [x] 5.2 记录 AnyImage 组名、Socket 与 identifier 对照结果；按用户决定暂缓 Shader identifier 修复，不阻塞 OmooNodes

## 验证记录

- 全量测试 59 项通过；本地构建曾验证 121 个资产；当前范围收敛为 O_Essentials/O_Extra 共 92 个资产，b52 远程库已通过验证，原生 listing 与摘要通过。
- 完整双版本开发库无修改回写通过；临时 b52 修改 O Scene Time 的 Step 后，仅新增对应 .b52.py，其他源码字节不变。
- Python 3.11 控制进程可调度独立 3.13 SDK 与 b52 环境；清除继承的 PYTHONHOME/PYTHONPATH，worker 使用隔离 Blender 用户目录。
- AnyImage 10 个公开组在临时目录完成 SDK 导出重建，Depth Cutout 逻辑一致；原工作区未改。
- AnyImage 的 O Image Layer、O Shadeless 逻辑一致，但 Socket identifier 重排。问题已记录；按用户决定，本次不继续处理 AnyImage，正式接入时另行验收。
- 1.4 已补充真实 bpy 往返、元数据与新增 Asset、共享图片冲突、源过期、并发修改、缺失 Asset 及候选失败测试。
- 图像签名覆盖 packed 数据、colorspace、alpha mode；Asset 签名覆盖作者、描述、标签、catalog、接口标识和适用的组属性。
- 父组因公共依赖变化而改变时仅更新基线，不重写父组源码；实际 b45 Step 修改仅改 O Scene Time 的通用文件与保留原 b52 实现的版本文件。
- 现有开发库在内容核对一致后升级基线；未改原 .blend，未覆盖人工修改。既有跨版本 Mix 求值差异诊断保留；本轮不恢复效果验证。Granules 继续延期。
- 项目环境为 Python 3.11、bpy 4.5.14，nodebpy 仅在独立后端安装；双版本开发库实跑成功。已知后端转存警告仅在成功转换时收起，4.5 Compositor 旧版存储通过原生临时写入释放，退出无内存泄漏提示，输入文件字节保持不变。
