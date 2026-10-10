## ADDED Requirements

### Requirement: 三个命令统一开发与正式构建

nodes SHALL 只提供 dev、build、dump 和各命令帮助。dev 默认准备完整开发节点库与基线；
--sync/-s SHALL 接收开发目录并验证回写，和显式 --output 互斥。build SHALL 从源码构建正式节点库，
dump SHALL 从节点库文件或目录导入来源。系统 MUST 不提供独立 sync/export/pack/catalog 或 docs nodes。

#### Scenario: 可选人工开发往返
- **WHEN** 用户 dev 准备开发库后在 Blender 修改，再 dev -s 回写
- **THEN** 验证后只更新变化源码，用户也可直接修改 .py 后 build，不依赖该开发环节

### Requirement: build 明确选择 local 与 remote

build SHALL 默认生成 local 节点库，--remote 切换到 remote；--self-contained SHALL 为本地库嵌入外部依赖。
--target 可选择已配置目标；省略构建全部配置目标。local SHALL 保留相对库引用并构建所需依赖库；
remote SHALL 自动本地化外部引用，同时传入 --self-contained SHALL 保持相同行为。
不受支持的 remote 目标 MUST 在修改正式产物前失败。

#### Scenario: 默认本地构建
- **WHEN** 用户执行 build --target b52
- **THEN** 构建完整 b52 本地库，不生成远程 listing

#### Scenario: 独立本地分发
- **WHEN** build nodes/O_Extra --self-contained
- **THEN** 外部依赖嵌入 O_Extra 本地库，不生成远程 listing，使用时无需另装依赖库

#### Scenario: 错误远程目标
- **WHEN** 显式 remote 选中不支持远程库的目标
- **THEN** 明确失败，不忽略该目标或自动改为 local

### Requirement: 正式节点库目录完整提交

build SHALL 输出分目标节点库目录，压缩包由项目发布流程负责。所有选定目标的构建和验证 SHALL
在临时目录完成，全部通过后提交；失败 MUST 保留原正式产物和人工编辑库。

#### Scenario: 双版本正式构建
- **WHEN** build -o dist 使用 b45/b52 配置
- **THEN** 得到 b45/b52 两套完整本地库目录

### Requirement: 所有消费者使用节点库

dev/build SHALL 保留公开根 Asset 标记，来源使用 collection.json 记录文件和依赖，公开根由原生 ASSET 定义。
AnyImage SHALL 以包含组及内部依赖的单文件本地节点库供插件按组名引用，不要求终端用户安装资产浏览器目录。
系统 MUST 不提供普通 blend 正式产物分支。

#### Scenario: 插件内节点引用
- **WHEN** AnyImage build --target b45
- **THEN** 得到带完整节点和依赖的本地库，插件打包程序从中取文件放入既有 assets 路径

### Requirement: dump 自动导入完整节点库

dump SHALL 接收 .blend 或节点库目录，要求 --output 来源位置，导入全部 Asset 根及所需辅助组，
保留依赖归属，不提供 --target 或 --names。首次导入的模块 SHALL 统一使用无版本后缀 .py，
MUST 不自动生成版本专用文件。工具 SHALL 记录原始文件的保存版本作为来源信息，不据此匹配目标或命名源码。
dump SHALL 验证转换往返；目标兼容性 SHALL 由后续 dev/build 验收，版本专用文件由开发者明确整理。
存在来源时 MUST 拒绝覆盖，已有开发修改通过 dev --sync 回写。没有 Asset 根时 MUST 明确报错。

#### Scenario: 首次导入统一无版本后缀
- **WHEN** dump 一个由 Blender 5.2 保存的节点库文件
- **THEN** 全部 Asset 根及辅助依赖导入无版本后缀 .py，记录原始保存版本，验证转换往返，不自动生成 .b52.py

#### Scenario: 首次迁移普通组
- **WHEN** 在 AnyImage 迁移副本中标记公开根后执行 dump
- **THEN** 全部 Asset 根通过实际验证后写入来源，原文件摘要不变


### Requirement: 同步覆盖元数据与共享资源并保护并发修改

系统 SHALL 将 Asset 元数据、接口标识、适用组属性、packed 图片内容和颜色设置纳入签名。
仅公共依赖变化时 SHALL 更新开发库基线，不重写消费者源码。
同步 SHALL 自动识别唯一工作区目标；多个目标存在时 MUST 要求显式选择。
修改 SHALL 回写现有通用或专用源码，不自动生成版本分支。共享源码与资源只需修改一个工作区，并对全部配置目标重建校验。
提交前 MUST 再次核对源与开发库摘要，发生并发修改时保留人工内容及原基线。

#### Scenario: 修改期间出现并发编辑
- **WHEN** 同步候选通过验证后，源码或开发目录被另一个操作者修改
- **THEN** 拒绝提交候选，不覆盖操作者的修改，不推进基线

#### Scenario: 图片颜色设置只在一个目标修改
- **WHEN** 共享图片在一个目标改为 Non-Color，其他目标保持原设置
- **THEN** 更新共享资源，对全部目标验证，通过后统一提交
