"""Read JSON records and replace staged library directories."""

import json
import shutil
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")


def replace_directories(replacements):
    """Commit directories together, restoring every old directory on failure."""
    backups = []
    installed = []
    try:
        for source, target in replacements:
            target.parent.mkdir(parents=True, exist_ok=True)
            backup = target.with_name(target.name + ".nodes-backup")
            if backup.exists():
                raise ValueError(f"Unfinished transaction: {backup}")
            if target.exists():
                target.rename(backup)
                backups.append((backup, target))
            installed.append(target)
            shutil.move(str(source), str(target))
    except Exception:
        for target in reversed(installed):
            if target.exists():
                shutil.rmtree(target)
        for backup, target in reversed(backups):
            backup.rename(target)
        raise
    for backup, _ in backups:
        shutil.rmtree(backup)
