#!/usr/bin/env python3
"""Read and validate a local copywriting knowledge catalog without modifying it."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

GROUPS = ("sources", "methods", "cases", "feedback")
BASE = {"id", "version", "title"}
REQUIRED = {
    "sources": BASE | {"kind", "reading_status", "reviewed_locations", "retrieved_at"},
    "methods": BASE | {"tags", "status", "source_refs", "rule", "applies_when", "limits", "steps", "checks", "validation_refs"},
    "cases": BASE | {"tags", "status", "source_refs", "case_type", "observations", "analysis", "outcome_evidence", "transfer_limits"},
    "feedback": BASE | {"kind", "evidence_type", "source_locator", "observation", "verified", "task_id"},
}


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def load(root_arg):
    skill_root = Path(__file__).resolve().parents[1]
    config_path = skill_root / "references/library-location.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    override = root_arg or os.environ.get("COPYWRITING_LIBRARY_ROOT")
    if override:
        root = Path(override).expanduser().resolve()
    else:
        root = (skill_root / Path(config["default_library_root"]).expanduser()).resolve()
    catalog = root / config["catalog"]
    if not catalog.is_file():
        raise ValueError("资料库不可读，请用 --library 指定已有资料库：" + str(catalog))
    data = json.loads(catalog.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("不支持的资料库格式")
    for group in GROUPS:
        if not isinstance(data.get(group), list):
            raise ValueError(group + " 必须是数组")
    return root, data


def all_records(data):
    return [(group, item) for group in GROUPS for item in data[group]]


def validate(root, data, check_files):
    errors, records = [], {}
    if not isinstance(data.get("revision"), int) or isinstance(data.get("revision"), bool) or data["revision"] < 1:
        errors.append("revision 需要为正整数")
    for group, item in all_records(data):
        if not isinstance(item, dict):
            errors.append(group + " 包含非对象条目")
            continue
        label = str(item.get("id", "无编号"))
        missing = REQUIRED[group] - item.keys()
        if missing:
            errors.append(label + " 缺少字段：" + ", ".join(sorted(missing)))
        if not isinstance(item.get("id"), str) or not item.get("id"):
            errors.append(label + " 的 id 无效")
        elif item["id"] in records:
            errors.append(label + " 编号重复")
        else:
            records[item["id"]] = (group, item)
        version = item.get("version")
        if not isinstance(version, int) or isinstance(version, bool) or version < 1:
            errors.append(label + " version 需要为正整数")

    sources = {s["id"]: s for s in data["sources"] if isinstance(s, dict) and "id" in s}
    feedback = {f["id"]: f for f in data["feedback"] if isinstance(f, dict) and "id" in f}
    for source in sources.values():
        sid = source["id"]
        if source.get("reading_status") not in {"registered", "metadata_only", "partial_review", "full_review"}:
            errors.append(sid + " 阅读状态无效")
        if source.get("kind") == "book":
            pages = source.get("pdf_pages")
            if not isinstance(pages, int) or isinstance(pages, bool) or pages < 1:
                errors.append(sid + " PDF 页数无效")
            if source.get("original_availability") == "citation_only":
                if "path" in source or "sha256" in source:
                    errors.append(sid + " 仅提供书目引用的记录应省去本地文件路径与指纹")
                continue
            rel = source.get("path")
            if not isinstance(rel, str) or Path(rel).is_absolute():
                errors.append(sid + " 需要库内相对路径")
                continue
            path = (root / rel).resolve()
            if not path.is_relative_to(root):
                errors.append(sid + " 文件越出资料库")
                continue
            if not re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", "")):
                errors.append(sid + " SHA-256 无效")
            if check_files:
                if not path.is_file():
                    errors.append(sid + " 原始文件缺失")
                elif hashlib.sha256(path.read_bytes()).hexdigest() != source.get("sha256"):
                    errors.append(sid + " 文件指纹变化，需重新核对来源版本")

    for group in ("methods", "cases"):
        for record in data[group]:
            if not isinstance(record, dict):
                continue
            rid = str(record.get("id", "无编号"))
            if record.get("status") not in {"reference", "candidate", "validated", "retired"}:
                errors.append(rid + " 成熟度状态无效")
            refs = record.get("source_refs")
            if not isinstance(refs, list) or not refs:
                errors.append(rid + " 需要来源引用")
                continue
            for ref in refs:
                source = sources.get(ref.get("source_id")) if isinstance(ref, dict) else None
                if not source:
                    errors.append(rid + " 引用了不存在的来源")
                    continue
                if source.get("kind") == "book":
                    reviewed = {p for loc in source.get("reviewed_locations", []) for p in loc.get("pdf_pages", [])}
                    used = ref.get("pdf_pages")
                    if not isinstance(used, list) or not used or any(not isinstance(p, int) or isinstance(p, bool) or p < 1 or p > source.get("pdf_pages", 0) or p not in reviewed for p in used):
                        errors.append(rid + " 引用页不在实际已读范围内")
            if record.get("status") == "validated":
                proof = record.get("validation_refs", [])
                if not proof or any(pid not in feedback or feedback[pid].get("verified") is not True for pid in proof):
                    errors.append(rid + " 缺少已核验反馈，不能标为 validated")
            if group == "cases" and record.get("case_type") in {"counterfactual_rewrite", "writing_exercise", "synthetic"}:
                if record.get("outcome_evidence", {}).get("verification_status") == "verified_market_result":
                    errors.append(rid + " 假设改写/练习不能标为真实市场结果")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", help="资料库根目录，置于子命令之前")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("summary")
    search = subs.add_parser("search")
    search.add_argument("query")
    search.add_argument("--kind", choices=GROUPS)
    search.add_argument("--limit", type=int, default=5)
    get = subs.add_parser("get")
    get.add_argument("id")
    check = subs.add_parser("validate")
    check.add_argument("--check-files", action="store_true", help="另核对库中保存的书籍原件和指纹")
    args = parser.parse_args()
    root, data = load(args.library)
    context = {"library": str(root), "catalog_revision": data["revision"]}
    if args.command == "summary":
        emit({**context, "counts": {g: len(data[g]) for g in GROUPS}, "sources": [{k: s.get(k) for k in ("id", "title", "reading_status", "pdf_pages", "coverage_note", "reviewed_locations")} for s in data["sources"]]})
    elif args.command == "get":
        matches = [(g, r) for g, r in all_records(data) if r.get("id") == args.id]
        if len(matches) != 1:
            raise ValueError("记录不存在或编号重复：" + args.id)
        emit({**context, "group": matches[0][0], "record": matches[0][1]})
    elif args.command == "search":
        terms = args.query.casefold().split()
        if not terms or not 1 <= args.limit <= 20:
            raise ValueError("需要关键词，limit 范围为 1-20")
        results = []
        for group, record in all_records(data):
            if args.kind and args.kind != group:
                continue
            if record.get("status") == "retired":
                continue
            text = " ".join(str(record.get(k, "")) for k in ("id", "title", "tags", "rule", "applies_when", "analysis", "author")).casefold()
            score = sum(text.count(term) for term in terms)
            if score:
                results.append({"group": group, "id": record["id"], "title": record["title"], "version": record["version"], "status": record.get("status", record.get("reading_status")), "score": score, "tags": record.get("tags", []), "source_refs": record.get("source_refs", []), "summary": record.get("rule", record.get("analysis", ""))[:240]})
        results.sort(key=lambda r: (-r["score"], r["id"]))
        emit({**context, "query": args.query, "total_matches": len(results), "results": results[:args.limit]})
    else:
        errors = validate(root, data, args.check_files)
        result = {**context, "ok": not errors, "checked_files": args.check_files, "counts": {g: len(data[g]) for g in GROUPS}, "errors": errors}
        if args.check_files:
            books = [source for source in data["sources"] if isinstance(source, dict) and source.get("kind") == "book"]
            citation_only = [source.get("id", "无编号") for source in books if source.get("original_availability") == "citation_only"]
            result["local_book_count"] = len(books) - len(citation_only)
            result["citation_only_books"] = citation_only
        emit(result)
        return 1 if errors else 0
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError) as exc:
        emit({"ok": False, "error": str(exc)})
        raise SystemExit(2)
