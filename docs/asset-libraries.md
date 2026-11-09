# 资产库

`O` 以 Blender 原生资产库的形式分发，无需安装插件。

## 选择安装方式

| Blender 版本 | 本地资产包 | 在线资产库 |
| --- | --- | --- |
| `4.5` 到 `5.1` | 支持 | 不支持 |
| `5.2` 及以上 | 支持 | 支持 |

本地资产包适合离线使用、固定版本或自行管理文件；在线资产库由 Blender 管理
在线 listing 与按需下载，适合 Blender 5.2 及以上版本。

## Blender 5.2 在线资产库

将 b52 资产包部署到资产服务器后，可以使用下方地址添加资产库。在线资产库在 Blender 5.2 中属于实验性功能，需要先启用对应选项。

1. 打开 `Edit > Preferences > Experimental`，启用`在线资产库`。
2. 打开 Preferences 的 `Assets` 页面。
3. 点击添加按钮，选择`添加在线资产库`。
4. 添加下列资产库。
5. 如果 Blender 提示需要网络访问，允许 Online Access。
6. 打开 Asset Browser，从资产库列表选择 `O`。

| 名称 | URL |
| --- | --- |
| `O` | `https://assets.omoolab.xyz/b52/O` |

URL 中的 `b52` 表示 Blender 5.2 资产版本。使用本地资产包时，选择不高于当前 Blender 版本的资产包。

首次打开时 Blender 需要下载 listing 和缩略图，可能需要等待片刻。资产文件会在使用时按需
下载并由 Blender 缓存。

远程资产由 Blender 缓存到本地后加载，因此运行时出现本地缓存路径属于正常行为。

## 本地资产库

本地安装沿用 Blender 的传统 Asset Library 工作流：

1. 从 [GitHub Releases](https://github.com/OmooLab/OmooNodes/releases) 或 [Gumroad](https://icrdr.gumroad.com/l/omoonodes) 下载对应版本的资产包。
2. 将 `O` 文件夹完整解压到固定位置。
3. 在 Blender Preferences 中找到 Asset Libraries。
4. 使用 `Add Local Asset Library` 添加 `O` 文件夹，将资产库命名为 `O`。
5. 打开 Asset Browser，从资产库列表选择 `O`。

Blender 5.2 的入口位于 Preferences 的 `Assets` 页面；Blender 4.5 到 5.1 的入口位于
`Edit > Preferences > File Paths > Asset Libraries`。

## 当前分类

- O Attribute
- O Debug
- O Deform
- O Edge
- O Filter
- O Generate
- O Read
- O Shader
- O Texture
- O Utilities
