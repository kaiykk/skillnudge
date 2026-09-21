"""Stable user-facing SkillNudge command dispatch."""

from __future__ import annotations

import os
import sys
import argparse


def _has_database_argument(argv: list[str]) -> bool:
    return "--database" in argv or any(
        item.startswith("--database=") for item in argv
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args in (["--help"], ["-h"]):
        parser = argparse.ArgumentParser(prog="skillnudge")
        subparsers = parser.add_subparsers(dest="command")
        subparsers.add_parser("advise", help="run the Phase 1 capability advisor")
        subparsers.add_parser("bootstrap", help="build the default local corpus/index")
        subparsers.add_parser(
            "retrieve",
            help="run provider-free Native Mode retrieval from a planning envelope",
        )
        parser.print_help()
        return 0
    if args and args[0] == "bootstrap":
        from .bootstrap import main as bootstrap_main

        return bootstrap_main(args[1:])
    if args and args[0] == "advise":
        if (
            "--help" not in args
            and "-h" not in args
            and not _has_database_argument(args)
            and not os.environ.get("SKILLNUDGE_DATABASE")
        ):
            from .bootstrap import bootstrap_default_index

            database_path = bootstrap_default_index().database_path
            args.extend(["--database", database_path])
        from .phase1 import main as phase1_main

        return phase1_main(args)
    if args and args[0] == "retrieve":
        from .native import main as native_main

        return native_main(args[1:])
    from .phase1 import main as phase1_main

    return phase1_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
