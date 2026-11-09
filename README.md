# Omoo Nodes

![cover](docs/assets/cover.png)

Omoo Nodes provides `O`, a practical node asset library created by OmooLab for
Blender. It turns frequently used workflows into reusable node groups, reducing the
time spent rebuilding common functionality while making complex node trees clearer
and easier to maintain.

Inspired in part by Houdini's procedural workflow, it is designed for real production
scenarios such as procedural modeling, particle effects, stylized non-photorealistic
rendering, scientific visualization, and annotation.

## Features

The library groups utilities, procedural modeling nodes, and artistic effects into categories such as `O Deform` and `O Generate`.

All nodes use Blender's native Asset Library system, with no add-on required.

The repository also provides the `omoonodes` Python package and its `omoonodes` CLI to
convert Python definitions to and from `.blend` files and build node libraries for
Blender 4.5 and 5.2. Other projects can use the same tool with their own node sources.

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

### Python Package and CLI

In a consuming project, install a fixed commit from this repository:

```bash
uv add --dev "omoonodes @ git+https://github.com/OmooLab/OmooNodes.git@<commit>"
```

Replace `<commit>` with the full commit SHA and commit `pyproject.toml` and `uv.lock`.
CI installs the same version with `uv sync --locked`. See the
[package guide](src/omoonodes/README.md) for configuration and usage, and the
[development guide](docs/develop.en.md) for this repository's workflow.
