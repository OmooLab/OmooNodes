# Development

## Environment and configuration

```bash
uv sync --locked --dev
uv run pytest tests
```

This repository contains the node asset libraries and the installable `omoonodes` package. `src/omoonodes/` provides the `omoonodes` command, configured by the calling project's `pyproject.toml`:

```toml
[tool.omoonodes]
targets = ["b45", "b52"]
```

Defaults: Python 3.11 / bpy 4.5.14 for b45; Python 3.13 / bpy 5.2.2 for b52.
uv prepares native target environments in `.cache/nodes/`. Each target builds, exports, saves, and checks its own files.
`tool.omoonodes.versions` overrides exact bpy versions. Input files and their dependencies must match the target major/minor version.

Commands show `...` while working, `✔` on completion, and output directories at the end. Blender Info, Warning, read-path messages, and leak statistics on successful exit are hidden; other Error messages or unsuccessful exits stop the command.

## Node development

`nodes/<library>/` contains Python, resources, catalogs, and `collection.json` describing files and dependencies.
Sources use nodebpy-style node classes, Socket expressions, and `>>` links, imported from `omoonodes`. `dev` and `build` arrange nodes automatically; sources contain no node positions or layout options.
Cross-library references import node classes through `nodes.<library>.<source>...`. The CLI loads sources for the selected target and reuses external links declared in `collection.json`.
Shared implementations use `.py`; b52-specific implementations use `.b52.py`. Related libraries share one target parent directory.

```bash
# Import assets and dependencies into a new source directory
uv run omoonodes dump path/to/O_Library.blend -o nodes/O_Library

# Build and overwrite development libraries
uv run omoonodes dev nodes/O_Extra -o workspaces

# Export development libraries, overwriting Python sources and resources
uv run omoonodes dev nodes/O_Extra -s workspaces

# Build local libraries and dependencies
uv run omoonodes build nodes/O_Extra --target b45 -o contents

# Standalone local libraries with embedded dependencies
uv run omoonodes build nodes/O_Extra --target b45 --self-contained -o contents

# Remote libraries with dependencies, native listings, metadata, thumbnails, and SHA-256
uv run omoonodes build --target b52 --remote -o dist
```

People edit development libraries in Blender; AI edits sources directly. The operator chooses the overwrite direction. Export also removes sources for deleted assets.
dev defaults to the lowest target; build defaults to all targets. Sync selects the unique workspace target, requiring --target when several exist.
Omitted sources use `tool.omoonodes.source`, defaulting to `nodes`. Default outputs are `workspaces/<target>/<library>/` and `dist/<target>/<library>/`.
Builds use temporary directories, save and reload in the target Blender, then replace outputs. CI archives the results for release.


## Publishing the Python package

`.github/workflows/push-main.yml` tests the source, builds the package, and checks isolated installations on pushes to main and pull requests targeting main.

`.github/workflows/publish.yml` runs on `v*` tags, tests the source, builds and checks the sdist and wheel, and publishes `omoonodes` through PyPI Trusted Publishing. The package version comes from `pyproject.toml`.

Before the first release, create a GitHub environment named `pypi` and add a pending publisher at [PyPI Publishing](https://pypi.org/manage/account/publishing/) with project `omoonodes`, owner `OmooLab`, repository `OmooNodes`, workflow `publish.yml`, and environment `pypi`. The first successful upload creates the PyPI project; no API token is needed.

Commit the version and lockfile, then push the matching tag, for example:

```bash
git tag v0.1.0
git push github v0.1.0
```

The same tag also triggers the existing node asset library release workflow.

## Documentation

```bash
uv run python -m tools.docs test    # Strict build in a temporary directory
uv run python -m tools.docs dev     # Local preview
uv run python -m tools.docs build  # Build major.minor.x and commit to local gh-pages
uv run python -m tools.docs deploy # Push to the github remote
```

Node documentation lives in `docs/nodes/`; the machine reference is `.agents/skills/use-omoo-nodes/references/node-catalog.json`.

Source definitions import `omoonodes`; see `src/omoonodes/README.md` for the small Python API. Unchanged content is not rewritten. Shared edits must build in every inheriting target before sources are replaced. Existing `.b52.py` implementations remain target-specific; `DISABLED = True` disables an asset for that target. Structural checks do not establish effect equivalence.
