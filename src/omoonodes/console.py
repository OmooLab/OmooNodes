"""Short progress messages for node commands."""

import sys
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from pathlib import Path


@contextmanager
def progress(label, indent=""):
    pending = f"{indent}{label} ..."
    interactive = sys.stdout.isatty()
    print(pending, end="" if interactive else "\n", flush=True)
    diagnostics = StringIO()
    try:
        with redirect_stdout(diagnostics):
            yield
    finally:
        if interactive:
            print("\r" + " " * len(pending) + "\r", end="")
        print(diagnostics.getvalue(), end="", flush=True)
    print(f"{indent}✔ {label}", flush=True)


def done(paths):
    print("Done", flush=True)
    for path in paths:
        path = Path(path).resolve()
        if path.is_relative_to(Path.cwd()):
            path = path.relative_to(Path.cwd())
        print(f"  - {path.as_posix()}", flush=True)
