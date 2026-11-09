# Omoo Nodes

![cover](assets/cover.png)

Omoo Nodes provides `O`, a practical node asset library for
Blender. It turns frequently used workflows into reusable node groups, reducing the
time spent rebuilding common functionality while making complex node trees clearer
and easier to maintain.

Inspired in part by Houdini's procedural workflow, it is designed for real production
scenarios such as procedural modeling, particle effects, stylized non-photorealistic
rendering, scientific visualization, and annotation.

## Features

The library groups utilities, procedural modeling nodes, and artistic effects into categories such as `O Deform` and `O Generate`.

All nodes use Blender's native Asset Library system, with no add-on required.

## Installation

Choose an installation method based on your Blender version and preferred workflow:

### Local Asset Library

1. Download the package for your Blender version from [GitHub Releases](https://github.com/OmooLab/OmooNodes/releases).
2. Extract the `O` folder to a permanent location.
3. Open `Edit > Preferences > Asset Libraries`.
4. Click `+`, select the `O` folder, and name the library `O`.

Keep the `.blend` files together inside the `O` folder.

### Remote Asset Library (5.2)

After the b52 archive has been deployed to the asset server, add the library at the URL below.

1. Open `Edit > Preferences > Asset Libraries`.
2. Click `+` on the right side of the list, select `Add Remote Asset Library`, and
   enter the URL of the asset library you need.

| Asset Library | URL |
| --- | --- |
| `O` | `https://assets.omoolab.xyz/b52/O` |

If Blender requests network permission, allow Online Access. Blender first loads the
asset listings and thumbnails, then downloads and caches individual assets on demand.
