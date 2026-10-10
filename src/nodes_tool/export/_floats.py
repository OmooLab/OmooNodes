# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
import math
from functools import lru_cache
import numpy as np

@lru_cache(maxsize=4096)
def fmt_float(value: float) -> str:
    if not math.isfinite(value):
        return repr(value)
    f32 = np.float32(value)
    if float(f32) != value:
        return repr(value)
    return np.format_float_positional(f32, unique=True, trim='0')
