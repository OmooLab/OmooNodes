# Development

## Environment and configuration

```bash
uv sync --locked --dev
uv run pytest tests
```

`tools/nodes/` provides the `nodes` command, configured by the calling project's `pyproject.toml`:

```toml
[tool.nodes]
targets = ["b45", "b52"]
```

Defaults: Python 3.11 / bpy 4.5.14 for b45; Python 3.13 / bpy 5.2.2 for b52.
The conversion backend uses Python 3.13 / bpy 5.2.2 / nodebpy 520.34.1. uv prepares environments in `.cache/nodes/`.
`tool.nodes.versions` overrides declared target versions; `tool.nodes.backend` overrides backend versions.

Commands show `...` while working, `✔` on completion, and output directories at the end. Blender Info, Warning, read-path messages, and leak statistics on successful exit are hidden; other Error messages or unsuccessful exits stop the command.

## Node development

`nodes/<library>/` contains Python, resources, catalogs, and `collection.json` describing files and dependencies.
Shared implementations use `.py`; b52-specific implementations use `.b52.py`. Related libraries share one target parent directory.

```bash
# Import assets and dependencies into a new source directory
uv run nodes dump path/to/O_Library.blend -o nodes/O_Library

# Build and overwrite development libraries
uv run nodes dev nodes/O_Extra -o workspaces

# Export development libraries, overwriting Python sources and resources
uv run nodes dev nodes/O_Extra -s workspaces

# Build local libraries and dependencies
uv run nodes build nodes/O_Extra --target b45 -o contents

# Standalone local libraries with embedded dependencies
uv run nodes build nodes/O_Extra --target b45 --self-contained -o contents

# Remote libraries with dependencies, native listings, metadata, thumbnails, and SHA-256
uv run nodes build --target b52 --remote -o dist
```

People edit development libraries in Blender; AI edits sources directly. The operator chooses the overwrite direction. Export also removes sources for deleted assets.
dev defaults to the lowest target; build defaults to all targets. Sync selects the unique workspace target, requiring --target when several exist.
Omitted sources use `tool.nodes.source`, defaulting to `nodes`. Default outputs are `workspaces/<target>/<library>/` and `dist/<target>/<library>/`.
Builds use temporary directories, save and reload in the target Blender, then replace outputs. CI archives the results for release.

All 92 assets pass a complete b52 roundtrip. The b52 backend migrates O Stroke, O Mix Color, and other nodes when opening b45 files; use --target b52 for complete roundtrips.

## Documentation

```bash
uv run docs test    # Strict build in a temporary directory
uv run docs dev     # Local preview
uv run docs build  # Build major.minor.x and commit to local gh-pages
uv run docs deploy # Push to the github remote
```

Node documentation lives in `docs/nodes/`; the machine reference is `.agents/skills/use-omoo-nodes/references/node-catalog.json`.
