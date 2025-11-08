"""Check SQLAlchemy model signature against stored snapshot.

If mismatch found, exit with code 1 and ask to generate a new Alembic
migration.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure app path importable
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.models.base import Base  # type: ignore
from app import models as _app_models  # noqa: F401  (import to populate metadata)

SNAPSHOT_PATH = BASE_DIR / "alembic" / "model_signature.json"


def build_signature() -> Dict[str, Any]:
    signature: Dict[str, Any] = {}
    for table in sorted(Base.metadata.sorted_tables, key=lambda t: t.name):
        cols = []
        for c in table.columns:
            col_def = {
                "name": c.name,
                "type": str(c.type),
                "nullable": c.nullable,
                "primary_key": c.primary_key,
            }
            cols.append(col_def)
        signature[table.name] = cols
    return signature


def main() -> int:
    current = build_signature()
    if not SNAPSHOT_PATH.exists():
        print("[model-check] snapshot not found, creating new one.")
        SNAPSHOT_PATH.write_text(
            json.dumps(current, indent=2, ensure_ascii=False)
        )
        return 0
    stored = json.loads(SNAPSHOT_PATH.read_text())
    if stored == current:
        print("[model-check] OK: model signature matches snapshot.")
        return 0
    # Compute diff summary
    added_tables = set(current.keys()) - set(stored.keys())
    removed_tables = set(stored.keys()) - set(current.keys())
    changed_tables = []
    for t in set(current.keys()) & set(stored.keys()):
        if current[t] != stored[t]:
            changed_tables.append(t)

    print("[model-check] MISMATCH detected.")
    if added_tables:
        print(f"  + Added tables: {', '.join(sorted(added_tables))}")
    if removed_tables:
        print(f"  - Removed tables: {', '.join(sorted(removed_tables))}")
    if changed_tables:
        print(f"  * Changed tables: {', '.join(sorted(changed_tables))}")
    print(
        "Please run: alembic revision --autogenerate -m 'update models' "
        "and update snapshot."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
