# Asset Libraries

`O` is distributed as a native Blender asset library and works without an add-on.

## Choose an Installation Method

| Blender Version | Local Package | Remote Asset Library |
| --- | --- | --- |
| `4.5` to `5.1` | Supported | Not supported |
| `5.2` and newer | Supported | Supported |

Use the local package for offline access, fixed versions, or direct file management.
With Blender 5.2 and newer, Remote Asset Libraries let Blender manage the online
listing, downloads, and cache.

## Blender 5.2 Remote Asset Libraries

After the b52 archive has been deployed to the asset server, add the library at the URL below. Remote Asset Libraries are experimental in Blender 5.2 and must first be enabled.

1. Open `Edit > Preferences > Experimental` and enable `Remote Asset Libraries`.
2. Open the `Assets` page in Preferences.
3. Click the add button and choose `Add Remote Asset Library`.
4. Add the library from the table below.
5. Allow Online Access if Blender requests network permission.
6. Open the Asset Browser and select `O`.

| Name | URL |
| --- | --- |
| `O` | `https://assets.omoolab.xyz/b52/O` |

The `b52` segment identifies the Blender 5.2 asset build.
For local packages, select a build that is not newer than the running Blender version.

The first load may take a moment while Blender downloads the listing and thumbnails.
Asset files are downloaded on demand and stored in Blender's cache.

Blender caches remote assets locally before loading them, so a local cache path
at runtime is expected.

## Local Asset Library

Local installation uses Blender's traditional Asset Library workflow:

1. Download the package for your Blender version from
   [GitHub Releases](https://github.com/OmooLab/OmooNodes/releases) or [Gumroad](https://icrdr.gumroad.com/l/omoonodes).
2. Extract the complete `O` folder to a permanent location.
3. Locate Asset Libraries in Blender Preferences.
4. Use `Add Local Asset Library` to add the `O` folder, then name the library `O`.
5. Open the Asset Browser and select `O`.

In Blender 5.2, use the `Assets` page in Preferences. In Blender 4.5 through 5.1, use
`Edit > Preferences > File Paths > Asset Libraries`.

## Current Catalogs

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
