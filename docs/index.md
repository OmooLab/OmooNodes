# 偶魔节点

![cover](assets/cover.png)

偶魔节点（Omoo Nodes）是 OmooLab 为 Blender 打造的一套实用节点资产库。它把工作中频繁
使用的流程封装成可复用的节点组，减少从头搭建常用功能的时间，也让复杂节点树更清晰、更易维护。

它部分借鉴了 Houdini 的程序化工作流，面向程序化建模、粒子特效、三渲二风格化、科学可视化和标识标注等真实制作场景；

## 功能与特色

整套资产按用途划分为多个资产库：

| 资产库 | 用途 |
| --- | --- |
| `O Essentials` | 基础功能节点与其他资产库的共享依赖 |
| `O Extra` | 程序化资产与特定艺术效果 |

所有节点都使用 Blender 原生资产库，无需安装插件

## 安装

根据 Blender 版本和使用方式选择安装方案：

### 本地资产库

1. 从 [Gumroad](https://icrdr.gumroad.com/l/omoonodes) 获取偶魔节点
2. 完整解压到固定目录
3. 打开 `编辑 > 偏好设置 > 资产库`
4. 点击列表右侧 `+`，选择资产库文件夹，比如 `O Essentials`

部分资产库依赖 `O Essentials`，解压后请保持相关资产库文件夹的相对位置不变。

### 远程资产库（5.2）

1. 打开 `编辑 > 偏好设置 > 资产库`
2. 点击列表右侧 `+`，选择`添加远程资产库`，输入需要的资产库的URL

| 资产库 | URL |
| --- | --- |
| `O Essentials` | `https://assets.omoolab.xyz/b52/O_Essentials` |
| `O Extra` | `https://assets.omoolab.xyz/b52/O_Extra` |

如果 Blender 请求网络权限，请允许 Online Access。Blender 会先读取资源列表和缩略图，
并在使用具体资产时按需下载和缓存文件。
