"""Load simulated TMS/SMMS/TDMS JSON files. Replace this module when real APIs exist."""

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_json(name: str) -> dict[str, Any]:
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_defect_sources() -> list[dict[str, Any]]:
    files = ["tms_defects.json", "smms_defects.json", "tdms_defects.json"]
    rows: list[dict[str, Any]] = []
    for name in files:
        payload = load_json(name)
        source = payload.get("source_system", "INTERNAL")
        for defect in payload.get("defects", []):
            item = dict(defect)
            item["source_system"] = source
            rows.append(item)
    return rows
