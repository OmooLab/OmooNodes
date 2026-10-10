# Development

## Environment

```bash
uv sync --locked --dev
uv run pytest tests
```

The shared `nodes` CLI is maintained in `tools/nodes/` in this repository.
The project uses Python 3.11 and bpy 4.5.14; nodebpy is installed only in the isolated backend.
The isolated backend defaults to Python 3.13, nodebpy 520.34.1, and bpy 5.2.2.
`tool.nodes.backend` may be omitted or override individual fields. Declare required targets explicitly:

```toml
[tool.nodes]
targets = ["b45", "b52"]

# Optional exact version override
[tool.nodes.versions]
b45 = "4.5.14"
```

Python is selected for the supported series: 3.11 for b45, 3.13 for b52.
Verified defaults are bpy 4.5.14 for b45 and 5.2.2 for b52; no live version lookup. Overrides cannot add undeclared targets. uv prepares isolated environments in `.cache/nodes/`.
The backend converts and arranges nodes; target workers inspect, save, reload, and clean libraries.
Workers use isolated Blender user directories and do not inherit Python paths from the controller.

## Sources

Only `O_Essentials` and `O_Extra` are currently managed in `nodes/`.

`nodes/<collection>/` contains native nodebpy Python, resources, catalogs, and `collection.json`.
Unversioned `.py` files are shared implementations expected to support the lowest configured target. `.b52.py` files contain
complete b52 implementations and take precedence for that target. Related libraries share one target parent directory.

## Commands

```bash
uv run nodes --help

# Import every asset node group and its dependencies into new sources
uv run nodes dump path/to/O_Library.blend -o nodes/O_Library

# Prepare full editable libraries and synchronize Blender changes
uv run nodes dev nodes/O_Extra -o workspaces
uv run nodes dev nodes/O_Extra --sync workspaces

# Build local libraries and their dependencies
uv run nodes build nodes/O_Extra --target b45 -o contents

# Embed dependencies for independent local distribution
uv run nodes build nodes/O_Extra --target b45 --self-contained -o contents

# Build remote libraries with native listings and embedded dependencies
uv run nodes build --target b52 --remote -o dist
```

For dev/build, omitted sources use `tool.nodes.source`, defaulting to `nodes`. Omitted targets
select the lowest target for dev and all targets for build. Sync reads one workspace target, requiring --target if several exist. dev defaults to `workspaces/<target>/<collection>/`;
build defaults to `dist/<target>/<collection>/`. You can edit Python and build directly.
Target versions can be overridden through `tool.nodes.versions` in `pyproject.toml`; `--target b52` selects one target.
dev reports dependencies, construction and layout, target saves, reload validation, and final output directories.
Status messages use English, with one build/save/check line per file. The expected newer-backend
conversion warning is hidden; the target saves, reloads, and checks the file version and node structure.
Other version warnings remain visible.
Sync reports change checks, export, version merging, rebuild validation, and commit, followed by updated source directories.
Sync replaces changed files and baselines, preserving source directories and editable blend files; failed commits restore file backups.
Normal empty-scene messages for asset-only files and read logs are hidden. Other warnings remain visible;
failed workers display their full diagnostics.
Long connections use horizontal channels, and development libraries retain multiple Group Inputs.

Initial dump always writes unversioned Python. The original file version is recorded as provenance;
target compatibility is checked separately by dev/build. Mark public roots as assets in a migration
copy before importing historical ordinary groups. Existing sources are updated through dev --sync.

Synchronization tracks asset metadata and packed image content/settings, ignores layout changes, checks source baselines, and validates rebuilt candidates
before committing. Edits return to their existing shared or specialized source; no implicit variants are created. Shared resources are edited in one target and validated across all configured targets. Source and workspace digests are checked again before commit. Changes inherited from public dependencies do not rewrite consumer modules. Formal build uses temporary directories, preserves editable workspaces, and
commits only after all selected targets succeed. Remote generation uses the pinned bpy package's
native module and validates listings, metadata, files, and SHA-256.

## CI and releases

Tag releases run tests, build b45 local libraries and b52 remote libraries, and archive each target
directory in CI. Granules remains deferred because of its missing dependency. Custom preview
restoration is deferred. Cross-version Mix conversion still needs verification; saving and reloading
alone does not establish full functional compatibility.

## Documentation

```bash
uv run docs test
uv run docs build
uv run docs dev
uv run docs deploy
```

`test` performs a strict temporary build, and `dev` starts a live preview. `build` creates the project's
major.minor.x series on local gh-pages; `deploy` pushes it to the github remote.
Existing node descriptions remain in `docs/nodes/`, and the machine reference remains in
`.agents/skills/use-omoo-nodes/references/node-catalog.json`.
