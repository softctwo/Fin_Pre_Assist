"""Compare FastAPI OpenAPI schema to stored snapshot."""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from fastapi import FastAPI


def load_app(import_path: str) -> FastAPI:
    if ":" not in import_path:
        raise ValueError("App import path must be in format 'module:attribute'")
    module_name, attr = import_path.split(":", 1)
    module = importlib.import_module(module_name)
    app = getattr(module, attr)
    if not isinstance(app, FastAPI):
        raise TypeError(f"{import_path} is not a FastAPI application")
    return app


def export_current_schema(app: FastAPI) -> Dict[str, Any]:
    # FastAPI caches openapi_schema; calling .openapi() ensures generation
    return app.openapi()


def flatten_paths(schema: Dict[str, Any]) -> List[str]:
    result: List[str] = []
    for path, methods in schema.get("paths", {}).items():
        if not isinstance(methods, dict):
            continue
        for method in methods.keys():
            result.append(f"{method.lower()} {path}")
    return sorted(result)


def collect_schema_names(schema: Dict[str, Any]) -> List[str]:
    comps = schema.get("components", {})
    schemas = comps.get("schemas", {}) if isinstance(comps, dict) else {}
    return sorted(schemas.keys())


def compute_diffs(current: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, Any]:
    current_paths = set(flatten_paths(current))
    snapshot_paths = set(flatten_paths(snapshot))
    current_schemas = set(collect_schema_names(current))
    snapshot_schemas = set(collect_schema_names(snapshot))

    return {
        "added_paths": sorted(current_paths - snapshot_paths),
        "removed_paths": sorted(snapshot_paths - current_paths),
        "added_schemas": sorted(current_schemas - snapshot_schemas),
        "removed_schemas": sorted(snapshot_schemas - current_schemas),
    }


def print_summary(diffs: Dict[str, Any]) -> None:
    for key in ("added_paths", "removed_paths", "added_schemas", "removed_schemas"):
        items = diffs.get(key) or []
        print(f"{key}: {len(items)}")
        for item in items:
            print(f"  - {item}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare OpenAPI schema to snapshot.")
    parser.add_argument("--app", default="app.main:app", help="FastAPI app import path")
    parser.add_argument(
        "--snapshot",
        default="docs/openapi_snapshot.json",
        help="Path to stored snapshot JSON",
    )
    parser.add_argument(
        "--diff-output",
        default="",
        help="Optional path to write diff JSON",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Write current schema to snapshot when differences are found",
    )
    args = parser.parse_args()

    app = load_app(args.app)
    current_schema = export_current_schema(app)

    snapshot_path = Path(args.snapshot)
    if not snapshot_path.exists():
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text(json.dumps(current_schema, indent=2, ensure_ascii=False))
        print(f"Snapshot not found. Created new snapshot at {snapshot_path}")
        return 0

    snapshot_schema = json.loads(snapshot_path.read_text())
    diffs = compute_diffs(current_schema, snapshot_schema)
    has_diff = any(diffs[key] for key in diffs)

    if args.diff_output:
        diff_path = Path(args.diff_output)
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.write_text(json.dumps(diffs, indent=2, ensure_ascii=False))

    if not has_diff:
        print("OpenAPI schema matches snapshot.")
        return 0

    print("Detected OpenAPI differences vs snapshot:")
    print_summary(diffs)

    if args.update:
        snapshot_path.write_text(json.dumps(current_schema, indent=2, ensure_ascii=False))
        print("Snapshot updated.")
        return 0

    print("Run with --update to refresh the snapshot.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
