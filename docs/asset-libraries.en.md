# Asset Libraries

OmooNodes is distributed as standard Blender Asset Libraries. No add-on needs to be
installed or enabled.

## Choose an Installation Method

| Blender Version | Local Package | Remote Asset Library |
| --- | --- | --- |
| `4.5` to `5.1` | Supported | Not supported |
| `5.2` and newer | Supported | Supported |

Use the local package for offline access, fixed versions, or direct file management.
With Blender 5.2 and newer, Remote Asset Libraries let Blender manage the online
listing, downloads, and cache.

## Blender 5.2 Remote Asset Libraries

Remote Asset Libraries are experimental in Blender 5.2 and must first be enabled.

1. Open `Edit > Preferences > Experimental` and enable `Remote Asset Libraries`.
2. Open the `Assets` page in Preferences.
3. Click the add button and choose `Add Remote Asset Library`.
4. Add each library from the table below.
5. Allow Online Access if Blender requests network permission.
6. Open the Asset Browser and select `O Essentials` or `O Extra`.

| Name | URL |
| --- | --- |
| `O Essentials` | `https://assets.omoolab.xyz/b52/O_Essentials` |
| `O Extra` | `https://assets.omoolab.xyz/b52/O_Extra` |

The `b52` segment identifies the Blender 5.2 asset build. Use only published URLs
listed in this documentation; do not mechanically substitute an unpublished version.
For local packages, select a build that is not newer than the running Blender version.

The first load may take a moment while Blender downloads the listing and thumbnails.
Asset files are downloaded on demand and stored in Blender's cache.

Blender caches remote assets locally before loading them, so a local cache path
at runtime is expected.

## Gumroad Local Asset Libraries

Local installation uses Blender's traditional Asset Library workflow:

1. Download the OmooNodes asset package from
   [Gumroad](https://icrdr.gumroad.com/l/omoonodes).
2. Extract the complete package to a permanent directory; do not copy only the
   `.blend` files.
3. Keep `O_Essentials` and `O_Extra` as sibling folders under the same parent.
4. Locate Asset Libraries in Blender Preferences.
5. Use `Add Local Asset Library` to add the `O_Essentials` and `O_Extra` folders
   separately.
6. Open the Asset Browser and select the library you want to use.

In Blender 5.2, use the `Assets` page in Preferences. In Blender 4.5 through 5.1, use
`Edit > Preferences > File Paths > Asset Libraries`.

!!! warning "Keep the Directory Structure"

    `O Extra` references core nodes from `O Essentials`. When moving the local
    libraries, move both folders together and preserve their sibling relationship.
    Do not rename or move only one of them.

## Current Catalogs

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
