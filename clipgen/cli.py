"""CLI entry point"""

import argparse
import sys
import yaml

from .engine import build, register_template, TEMPLATE_REGISTRY
from . import __version__


def list_templates():
    """Lazy-import all templates and print available ones."""
    from .engine import auto_import_templates
    auto_import_templates()
    print("Available templates:")
    for name in sorted(TEMPLATE_REGISTRY):
        print(f"  - {name}")


def main():
    parser = argparse.ArgumentParser(
        prog="clipgen",
        description="Short video auto generator — AI配音+字幕+画面一键生成",
    )
    parser.add_argument("--version", action="version", version=f"clipgen {__version__}")

    sub = parser.add_subparsers(dest="command", help="Commands")

    # build
    build_p = sub.add_parser("build", help="Build video from YAML config")
    build_p.add_argument("config", help="Path to YAML config file")
    build_p.add_argument("-o", "--output", help="Output video path (overrides config)")
    build_p.add_argument("-q", "--quiet", action="store_true", help="Suppress progress output")

    # templates
    sub.add_parser("templates", help="List available templates")

    args = parser.parse_args()

    if args.command == "build":
        with open(args.config, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if args.output:
            config["output"] = args.output

        try:
            out = build(config, verbose=not args.quiet)
            if not args.quiet:
                print(f"\n  Saved to: {out}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "templates":
        list_templates()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
