#!/usr/bin/env python3
"""
DALS Worker Forge CLI
Command-line interface for forging DALS workers using the registry system.
"""

import argparse
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from worker_forge.forge_engine import forge_worker
from workers.registry import list_registered_types

def main():
    parser = argparse.ArgumentParser(
        description="Forge DALS workers using the registry system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python forge_worker_cli.py --type goat --name my-goat-worker --class A1
  python forge_worker_cli.py --type mint --name mint-worker --class B2 --dry-run
  python forge_worker_cli.py --list-types

Available worker types:
  template, goat, mint, finance, ucm_relay, obs, telemetry, ledger, archival, mechanist
        """
    )

    parser.add_argument(
        "--type", "-t",
        help="Worker type to forge (use --list-types to see available types)"
    )

    parser.add_argument(
        "--name", "-n",
        help="Name for the worker instance"
    )

    parser.add_argument(
        "--class-code", "-c",
        help="Class code for the worker (e.g., A1, B2, C3)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry run without creating files"
    )

    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List all available worker types and exit"
    )

    args = parser.parse_args()

    # Handle list types request
    if args.list_types:
        print("Available worker types:")
        for worker_type in sorted(list_registered_types()):
            print(f"  - {worker_type}")
        return

    # Validate required arguments for forging
    if not args.type or not args.name or not args.class_code:
        parser.error("--type, --name, and --class-code are required when not using --list-types")

    # Validate worker type
    available_types = list_registered_types()
    if args.type not in available_types:
        print(f"Error: Worker type '{args.type}' is not registered.")
        print(f"Available types: {', '.join(sorted(available_types))}")
        sys.exit(1)

    # Forge the worker
    try:
        print(f"🔨 Forging worker: {args.name} (type: {args.type}, class: {args.class_code})")
        if args.dry_run:
            print("📋 Dry run mode - no files will be created")

        result = forge_worker(
            worker_name=args.name,
            worker_type=args.type,
            class_code=args.class_code,
            dry_run=args.dry_run
        )

        if args.dry_run:
            print("✅ Dry run completed successfully!")
            print(f"   Serial: {result['worker_serial']}")
            print(f"   Model: {result['worker_model']}")
            print(f"   Template: {result['template_used']}")
            print(f"   Port: {result['port']}")
        else:
            print("✅ Worker forged successfully!")
            print(f"   Serial: {result['serial']}")
            print(f"   Model: {result['model']}")
            print(f"   Location: workers/{args.name}/")
            print(f"   Template: WorkerTemplate")  # We know it's WorkerTemplate from registry

    except Exception as e:
        print(f"❌ Failed to forge worker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()