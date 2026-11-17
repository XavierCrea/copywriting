#!/usr/bin/env python3
"""Check reviewed English case pages against their maintained source records."""
import argparse
import hashlib
import json
from pathlib import Path

LIBRARY = Path(__file__).resolve().parents[1] / "copywriting-learning" / "library"


def fingerprint(case, data):
    source_ids = {ref["source_id"] for ref in case["source_refs"]}
    method_ids = set(case.get("method_ids", []))
    value = {
        "case": case,
        "sources": sorted((s for s in data["sources"] if s["id"] in source_ids), key=lambda x: x["id"]),
        "methods": sorted((m for m in data["methods"] if m["id"] in method_ids), key=lambda x: x["id"]),
    }
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def reviewed_record(case, data, path):
    return {
        "source_version": case["version"],
        "source_sha256": fingerprint(case, data),
        "english_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def check_translations(library=LIBRARY):
    data = json.loads((library / "catalog.json").read_text(encoding="utf-8"))
    manifest_path = library / "translations.en.json"
    if not manifest_path.exists():
        print("Missing English translation review manifest.")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {c["id"] for c in data["cases"]}
    actual = {p.stem for p in (library / "cases/en").glob("*.md")}
    errors = []
    for key in sorted(actual - expected):
        errors.append(f"Unexpected English page: {key}")
    for key in sorted(set(manifest) - expected):
        errors.append(f"Unexpected review record: {key}")
    for case in data["cases"]:
        key = case["id"]
        path = library / "cases/en" / f"{key}.md"
        if not path.exists():
            errors.append(f"Missing English page: {key}")
        elif manifest.get(key) != reviewed_record(case, data, path):
            errors.append(f"English review required: {key}")
        elif "## English writing craft" not in path.read_text(encoding="utf-8"):
            errors.append(f"Missing English writing craft: {key}")
    for error in errors:
        print(error)
    if not errors:
        print(f"English translations checked: {len(expected)} pages.")
    return int(bool(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="append", default=[], metavar="CASE_ID", help="Acknowledge a manually reviewed English page; repeat for several pages.")
    args = parser.parse_args()
    if args.record:
        data = json.loads((LIBRARY / "catalog.json").read_text(encoding="utf-8"))
        cases = {c["id"]: c for c in data["cases"]}
        path = LIBRARY / "translations.en.json"
        manifest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        updates = {}
        for key in args.record:
            if key not in cases:
                parser.error(f"Unknown case: {key}")
            page = LIBRARY / "cases/en" / f"{key}.md"
            if not page.is_file() or "## English writing craft" not in page.read_text(encoding="utf-8"):
                parser.error(f"Missing complete English page: {key}")
            updates[key] = reviewed_record(cases[key], data, page)
        manifest.update(updates)
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Recorded manual review for {len(updates)} English pages.")
    return check_translations()


if __name__ == "__main__":
    raise SystemExit(main())
