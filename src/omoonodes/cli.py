"""Parse commands for native node library development and publication."""

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

from . import importing, libraries
from .runtimes import project_root


def parser():
    result = argparse.ArgumentParser(prog="omoonodes", description="Develop, import, and build node libraries")
    commands = result.add_subparsers(dest="command", required=True)
    development = commands.add_parser("dev", help="Overwrite development libraries or sources")
    development.add_argument("source", nargs="?", type=Path, help="Collection or nodes root; defaults to project source")
    direction = development.add_mutually_exclusive_group()
    direction.add_argument("-o", "--output", type=Path, help="Overwrite development libraries here; defaults to workspaces")
    direction.add_argument("-s", "--sync", type=Path, help="Overwrite Python sources from this development parent")
    development.add_argument("--target", help="Dev: lowest configured target by default; sync: unique workspace target")
    formal = commands.add_parser("build", help="Build formal node libraries")
    formal.add_argument("source", nargs="?", type=Path, help="Collection or nodes root; defaults to project source")
    formal.add_argument("-o", "--output", type=Path, default=Path("dist"), help="Output parent; defaults to dist")
    formal.add_argument("--target", help="Configured target; defaults to all")
    formal.add_argument("--remote", action="store_true", help="Generate a remote library; default is local")
    formal.add_argument("--self-contained", action="store_true", help="Embed external dependencies in local libraries")
    importing = commands.add_parser("dump", help="Import all asset node groups as native sources")
    importing.add_argument("input", type=Path, help="Asset library blend file or directory")
    importing.add_argument("-o", "--output", type=Path, required=True, help="New native source destination")
    importing.add_argument("--target", help="Configured target; defaults to the lowest")
    return result


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf8")
    command = parser()
    args = command.parse_args(argv)
    try:
        if args.command == "dump":
            importing.dump_sources(args.input.resolve(), args.output.resolve(), args.target)
            return
        root = project_root()
        settings = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf8")).get("tool", {}).get("omoonodes", {})
        source = (args.source or root / settings.get("source", "nodes")).resolve()
        if args.command == "dev":
            if args.sync:
                libraries.sync(source, args.sync.resolve(), args.target)
            else:
                libraries.dev(source, (args.output or Path("workspaces")).resolve(), args.target)
        else:
            libraries.build(source, args.output.resolve(), args.target, args.remote, args.self_contained)
    except (ValueError, OSError, RuntimeError, subprocess.CalledProcessError) as error:
        command.exit(1, f"omoonodes: {error}\n")


if __name__ == "__main__":
    main()
