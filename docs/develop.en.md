# Development

This page documents the asset build and documentation workflows for OmooNodes.

## Environment

The project uses `uv` to manage its Python environment.

```bash
uv sync
uv run pytest tests
```

Build or preview the documentation with:

```bash
uv run mkdocs build
uv run mkdocs serve
```

## Directory Layout

```text
subspaces   Blender asset sources
contents    Cleaned local Asset Libraries
dist        Deployable Remote Asset Libraries
```

Each Asset Library has one source directory. An unversioned `.blend` file is the base
layer. A `.b<major><minor>.blend` file is an overlay enabled from that Blender version
onward. Same-named node groups override lower layers, while new names are added. The
Blender running the build selects the overlays. Output paths have no version layer.

For example:

```text
subspaces/O_Essentials/
├─ O_Essentials_GeometryNodes.blend
├─ O_Essentials_GeometryNodes.b52.blend
├─ O_Essentials_ShaderNodes.blend
└─ blender_assets.cats.txt
```

Blender 4.5 builds only the base layer. Blender 5.2 composes the base and `.b52.blend`
in order. An overlay may link common node groups from the base file. The build remaps
those references to local data in the result and replaces base node groups with
same-named overlay implementations.

### Version Composition Rules

- An unversioned file is the Blender 4.5 base layer. Do not create overlays older
  than `b45`.
- The Blender running the script determines the target version. A filename such as
  `.b52.blend` determines when an overlay is enabled; the file's saved version does
  not control selection.
- The build loads the base first, then applies every compatible overlay from the
  lowest version to the highest.
- New node groups are added. Same-named node groups replace lower-version
  implementations.

For example, Blender 5.3 composes `base → b52 → b53`, so a `b53` implementation wins
when names match.

## Run the Build Script

The target Blender must execute the script. These Git Bash examples store its
executable in a variable:

`build_assets.py` is a single-file tool that depends only on Blender's bundled `bpy`
and the Python standard library. The build environment does not need a separate
Python, `uv`, or project dependencies; distributing the build tool requires only this
script.

```bash
BLENDER="C:/path/to/blender.exe"
```

General invocation:

```bash
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- SOURCE [OPTIONS]
```

- `-b` runs Blender in background mode.
- `--python-exit-code 1` returns a non-zero status when Python fails.
- `-P build_assets.py` executes the build script.
- `--` separates Blender arguments from build-script arguments.
- `SOURCE` is one Asset Library source directory.
- `-o/--out` selects the output parent; the result keeps the `SOURCE` directory
  name.

Composition, cleanup, and validation happen in staging directories. The target is
replaced only after every step succeeds. Blender backups, old remote listings, and
temporary files are excluded.

## Build Local Asset Libraries

Local builds preserve linked libraries and their original relative paths by default.
Build `O_Essentials` first, then `O_Extra`, keeping both under the same output parent:

```bash
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Essentials -o contents
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Extra -o contents
```

The results are `contents/O_Essentials` and `contents/O_Extra`. Use
`--self-contained` to build a local library without external linked-library
dependencies:

```bash
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Extra --self-contained -o contents
```

## Build Remote Asset Libraries

Remote mode localizes linked datablocks, removes external references, generates the
listing, metadata, and thumbnails, and validates asset files and SHA-256 hashes:

Localization happens while source-relative paths are still valid. Dependency
datablocks keep their node contents without inheriting Asset marks from the source
library.

```bash
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Essentials --remote -o dist
"$BLENDER" -b --python-exit-code 1 -P build_assets.py -- \
  subspaces/O_Extra --remote -o dist
```

Remote builds validate asset counts, file counts, thumbnails, and SHA-256 hashes.
`--remote` already produces a result without external references, so it cannot be
combined with `--self-contained`.

Deployment mapping:

| Build Directory | Public URL |
| --- | --- |
| `dist/O_Essentials` | `https://assets.omoolab.xyz/b52/O_Essentials` |
| `dist/O_Extra` | `https://assets.omoolab.xyz/b52/O_Extra` |

## Node Documentation and the Codex Skill

Node metadata follows one directional synchronization flow:

```text
Published .blend files
  → .agents/skills/use-omoo-nodes/references/node-catalog.json
  → docs/nodes/o-essentials.md
  → docs/nodes/o-extra.md
```

`node-catalog.json` is the machine reference used by the skill. It stores exact node
names, tree types, socket identifiers, defaults, dependencies, and concise usage
descriptions. `docs/nodes/` contains the user-facing references generated from the same
catalog. Do not maintain duplicate node Markdown inside the skill.

Maintain node functions, practical use cases, and plain-language parameter explanations
in `scripts/generate_node_reference.py`. Node functions are also written to each
catalog `description`, while the docs receive the complete user-facing guide. After
updating assets, inspect the published libraries with the target Blender version, then
regenerate the catalog descriptions and documentation:

```bash
BLENDER="C:/path/to/blender.exe"

"$BLENDER" -b --python-exit-code 1 \
  -P scripts/inspect_omoo_nodes.py -- \
  dist/O_Essentials dist/O_Extra \
  --output .agents/skills/use-omoo-nodes/references/node-catalog.json

uv run python scripts/generate_node_reference.py \
  .agents/skills/use-omoo-nodes/references/node-catalog.json \
  dist \
  docs/nodes
```

The generator embeds `BEHAVIOR_NOTES` into each catalog `description` and rebuilds
both node reference pages. Generation fails when a new node has no usage description,
preventing silent drift between the skill and docs.

Finish by running the Blender integration check, skill validator, tests, and docs
build:

```bash
"$BLENDER" -b --python-exit-code 1 \
  -P scripts/validate_omoo_nodes_in_blender.py -- \
  dist dist/validation/use-omoo-nodes-validation.blend
uv run pytest tests/test_use_omoo_nodes_skill.py
uv run mkdocs build
```

Keep asset spelling exactly as published, including names such as `O Solidfy` and
`Rest Positon`.
