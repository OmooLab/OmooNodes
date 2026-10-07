# 资产库

OmooNodes 以标准 Blender Asset Library 的形式分发，不需要安装或启用 add-on。

## 选择安装方式

| Blender 版本 | 本地资产包 | 在线资产库 |
| --- | --- | --- |
| `4.5` 到 `5.1` | 支持 | 不支持 |
| `5.2` 及以上 | 支持 | 支持 |

本地资产包适合离线使用、固定版本或自行管理文件；在线资产库由 Blender 管理
在线 listing 与按需下载，适合 Blender 5.2 及以上版本。

## Blender 5.2 在线资产库

在线资产库在 Blender 5.2 中属于实验性功能，需要先启用对应选项。

1. 打开 `Edit > Preferences > Experimental`，启用`在线资产库`。
2. 打开 Preferences 的 `Assets` 页面。
3. 点击添加按钮，选择`添加在线资产库`。
4. 分别添加下列两个资产库。
5. 如果 Blender 提示需要网络访问，允许 Online Access。
6. 打开 Asset Browser，从资产库列表选择 `O Essentials` 或 `O Extra`。

| 名称 | URL |
| --- | --- |
| `O Essentials` | `https://assets.omoolab.xyz/b52/O_Essentials` |
| `O Extra` | `https://assets.omoolab.xyz/b52/O_Extra` |

URL 中的 `b52` 表示 Blender 5.2 资产版本。只使用本文列出的已发布地址，不要把版本号
机械替换成未经发布的地址。使用本地资产包时也应选择不高于当前 Blender 的对应版本。

首次打开时 Blender 需要下载 listing 和缩略图，可能需要等待片刻。资产文件会在使用时按需
下载并由 Blender 缓存。

远程资产由 Blender 缓存到本地后加载，因此运行时出现本地缓存路径属于正常行为。

## Gumroad 本地资产库

本地安装沿用 Blender 的传统 Asset Library 工作流：

1. 从 [Gumroad](https://icrdr.gumroad.com/l/omoonodes) 下载 OmooNodes 资产包。
2. 将资产包完整解压到固定目录，不要只复制其中的 `.blend` 文件。
3. 保持 `O_Essentials` 与 `O_Extra` 为同一父目录下的兄弟文件夹。
4. 在 Blender Preferences 中找到 Asset Libraries。
5. 分别使用 `Add Local Asset Library` 添加 `O_Essentials` 和 `O_Extra` 文件夹。
6. 打开 Asset Browser，从资产库列表选择需要的资产库。

Blender 5.2 的入口位于 Preferences 的 `Assets` 页面；Blender 4.5 到 5.1 的入口位于
`Edit > Preferences > File Paths > Asset Libraries`。

!!! warning "保持目录结构"

    `O Extra` 会引用 `O Essentials` 中的基础节点。移动本地资产库时，应同时移动两个
    文件夹并保持它们的兄弟目录关系；不要单独重命名或移动其中一个文件夹。

## 当前分类

### O Essentials

- Attribute
- Curve
- Debug
- Deform
- Filter
- Generate
- Read
- Texture
- Utilities

### O Extra

- Effect
- Misc
- Scene
