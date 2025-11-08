"""Summarize coverage for backend (coverage.py XML) and frontend (Vitest v8).

Outputs GitHub Action outputs: backend, frontend, total.
Optionally writes a simple SVG badge when --badge path is provided.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def read_backend_coverage_xml(path: Path) -> float | None:
    if not path.exists():
        return None
    try:
        root = ET.parse(path).getroot()
        line_rate = root.get("line-rate")
        if line_rate is None:
            return None
        return round(float(line_rate) * 100.0, 2)
    except Exception:
        return None


def _get_total_pct_from_v8_total(data: dict) -> float | None:
    total = data.get("total") if isinstance(data, dict) else None
    if total and isinstance(total, dict):
        for key in ("statements", "lines"):
            section = total.get(key)
            if section and isinstance(section, dict):
                pct = section.get("pct")
                if pct is not None:
                    return round(float(pct), 2)
    return None


def _avg_file_level_pct(data: dict) -> float | None:
    if not isinstance(data, dict):
        return None
    pcts = []
    for k, v in data.items():
        if k == "total" or not isinstance(v, dict):
            continue
        section = v.get("statements") or v.get("lines")
        if isinstance(section, dict):
            pct_val = section.get("pct")
            if pct_val is not None:
                pcts.append(float(pct_val))
    if pcts:
        return round(sum(pcts) / len(pcts), 2)
    return None


def read_frontend_coverage_json(path: Path) -> float | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return _get_total_pct_from_v8_total(data) or _avg_file_level_pct(data)
    except Exception:
        return None


def pick_badge_color(pct: float) -> str:
    if pct >= 90:
        return "#4c1"  # brightgreen
    if pct >= 80:
        return "#a3c51c"  # yellowgreen
    if pct >= 70:
        return "#dfb317"  # yellow
    if pct >= 60:
        return "#fe7d37"  # orange
    return "#e05d44"  # red


def generate_badge_svg(pct: float) -> str:
    # Simple static-width badge to avoid complex text measurements
    color = pick_badge_color(pct)
    label = "coverage"
    value = f"{pct:.0f}%"
    # Fixed layout ~ (label 70 + value 54) width
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="124" height="20" role="img"
    aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="m"><rect width="124" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#m)">
    <rect width="70" height="20" fill="#555"/>
    <rect x="70" width="54" height="20" fill="{color}"/>
    <rect width="124" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle"
      font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="35" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="35" y="14">{label}</text>
    <text x="96" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="96" y="14">{value}</text>
  </g>
</svg>
""".strip()


def write_step_summary(
    backend_pct: float | None,
    frontend_pct: float | None,
    total_pct: float | None,
) -> None:
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    lines = ["## Coverage Summary", ""]
    if backend_pct is None:
        lines.append("- Backend: N/A")
    else:
        lines.append(f"- Backend: {backend_pct:.2f}%")
    if frontend_pct is None:
        lines.append("- Frontend: N/A")
    else:
        lines.append(f"- Frontend: {frontend_pct:.2f}%")
    if total_pct is None:
        lines.append("- Total: N/A")
    else:
        lines.append(f"- Total: {total_pct:.2f}%")
    Path(summary_path).write_text("\n".join(lines), encoding="utf-8")


def export_github_outputs(
    backend_pct: float | None,
    frontend_pct: float | None,
    total_pct: float | None,
) -> None:
    gha_output = os.getenv("GITHUB_OUTPUT")
    if not gha_output:
        return
    with open(gha_output, "a", encoding="utf-8") as f:
        if backend_pct is not None:
            f.write(f"backend={backend_pct}\n")
        if frontend_pct is not None:
            f.write(f"frontend={frontend_pct}\n")
        if total_pct is not None:
            f.write(f"total={total_pct}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", type=str, default="backend/coverage.xml")
    parser.add_argument(
        "--frontend",
        type=str,
        default="frontend/coverage/coverage-final.json",
    )
    parser.add_argument("--badge", type=str, default="")
    args = parser.parse_args()

    backend_path = Path(args.backend)
    frontend_path = Path(args.frontend)
    badge_path = Path(args.badge) if args.badge else None

    backend_pct = read_backend_coverage_xml(backend_path)
    frontend_pct = read_frontend_coverage_json(frontend_path)

    # Compute total as simple average of available values
    values = [v for v in (backend_pct, frontend_pct) if v is not None]
    total_pct = round(sum(values) / len(values), 2) if values else None

    # Emit GitHub Action outputs if available
    export_github_outputs(backend_pct, frontend_pct, total_pct)

    # Also export to environment for subsequent steps if desired
    if backend_pct is not None:
        print(f"BACKEND_COVERAGE={backend_pct}")
        os.environ["BACKEND_COVERAGE"] = str(backend_pct)
    if frontend_pct is not None:
        print(f"FRONTEND_COVERAGE={frontend_pct}")
        os.environ["FRONTEND_COVERAGE"] = str(frontend_pct)
    if total_pct is not None:
        print(f"TOTAL_COVERAGE={total_pct}")
        os.environ["TOTAL_COVERAGE"] = str(total_pct)

    # Write summary markdown when possible
    write_step_summary(backend_pct, frontend_pct, total_pct)

    # Generate badge if requested (fallback to backend only)
    badge_value = total_pct or backend_pct or 0.0
    if badge_path:
        badge_path.parent.mkdir(parents=True, exist_ok=True)
        svg_content = generate_badge_svg(badge_value)
        badge_path.write_text(svg_content, encoding="utf-8")

    # Always succeed; this script should not fail the build
    return 0


if __name__ == "__main__":
    sys.exit(main())
