import gzip

import pytest
import zstandard

from omoonodes.blend import check_version, file_version


@pytest.mark.parametrize("header,version", [(b"BLENDER-v405", (4, 5)), (b"BLENDER17-01v0502", (5, 2))])
@pytest.mark.parametrize("compression", [bytes, gzip.compress, zstandard.ZstdCompressor().compress])
def test_version_preflight_handles_native_and_compressed_headers(tmp_path, header, version, compression):
    path = tmp_path / "library.blend"
    path.write_bytes(compression(header + b"\0" * 30))
    assert file_version(path) == version
    check_version(path, (*version, 99))
    with pytest.raises(ValueError, match="saved by Blender"):
        check_version(path, (9, 9, 0))
