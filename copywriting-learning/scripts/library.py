#!/usr/bin/env python3
"""Search, validate, and apply reviewed changes to a local copywriting catalog."""

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import unicodedata

GROUPS = ("sources", "methods", "cases", "feedback")
LEARNING_ORIGINS = {"book_canon", "benchmark_study", "co_dissected_teardown", "task_feedback"}
BASE = {"id", "version", "title"}
REQUIRED = {
    "sources": BASE | {"kind", "reading_status", "reviewed_locations", "retrieved_at"},
    "methods": BASE | {"tags", "status", "source_refs", "rule", "applies_when", "limits", "steps", "checks", "validation_refs"},
    "cases": BASE | {"tags", "status", "source_refs", "case_type", "observations", "analysis", "outcome_evidence", "transfer_limits"},
    "feedback": BASE | {"kind", "evidence_type", "source_locator", "observation", "verified", "task_id"},
}
TOKEN = re.compile(r"[a-z0-9]+|[\u3400-\u9fff]+")
HAN = re.compile(r"[\u3400-\u9fff]")
SAFE_ID = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")
STOP_WORDS = set(
    "a an and are as at be but by can could do does for from had has have how i in is it "
    "me my of on or our should that the their them they this to us was we were what when where "
    "which who why will with would you your s t".split()
)


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def locate_catalog(root_arg):
    skill_root = Path(__file__).resolve().parents[1]
    config_path = skill_root / "references/library-location.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    override = root_arg or os.environ.get("COPYWRITING_LIBRARY_ROOT")
    if override:
        root = Path(override).expanduser().resolve()
    else:
        root = (skill_root / Path(config["default_library_root"]).expanduser()).resolve()
    catalog = (root / config["catalog"]).resolve()
    if not catalog.is_relative_to(root):
        raise ValueError("资料库索引必须在资料库目录内")
    if not catalog.is_file():
        raise ValueError("资料库不可读，请用 --library 指定已有资料库：" + str(catalog))
    return root, catalog


def parse_catalog(contents):
    data = json.loads(contents)
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("不支持的资料库格式")
    for group in GROUPS:
        if not isinstance(data.get(group), list):
            raise ValueError(group + " 必须是数组")
    return data


def all_records(data):
    return [(group, item) for group in GROUPS for item in data[group]]


def has_text(value):
    return isinstance(value, str) and bool(value.strip())


def text_list(value):
    return isinstance(value, list) and all(has_text(item) for item in value)


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
        if not has_text(item.get("id")):
            errors.append(label + " 的 id 无效")
        elif item["id"] in records:
            errors.append(label + " 编号重复")
        else:
            records[item["id"]] = (group, item)
        version = item.get("version")
        if not isinstance(version, int) or isinstance(version, bool) or version < 1:
            errors.append(label + " version 需要为正整数")
        if not has_text(item.get("title")):
            errors.append(label + " 的 title 不能为空")
        if "title_en" in item and not has_text(item["title_en"]):
            errors.append(label + " 的 title_en 不能为空")
        if "tags_en" in item and not text_list(item["tags_en"]):
            errors.append(label + " 的 tags_en 必须为非空字符串的数组")
        if "when_stuck" in item:
            symptoms = item["when_stuck"]
            if not isinstance(symptoms, dict) or set(symptoms) != {"zh", "en"} or any(
                not text_list(values) or not values for values in symptoms.values()
            ):
                errors.append(label + " 的 when_stuck 需要 zh、en 各一组非空症状")

    sources = {key: item for key, (group, item) in records.items() if group == "sources"}
    feedback = {key: item for key, (group, item) in records.items() if group == "feedback"}
    methods = {key for key, (group, _) in records.items() if group == "methods"}
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
            digest = source.get("sha256")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
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
            if not text_list(record.get("tags")):
                errors.append(rid + " 的 tags 必须为非空字符串的数组")
            refs = record.get("source_refs")
            if not isinstance(refs, list) or not refs:
                errors.append(rid + " 需要来源引用")
                continue
            for ref in refs:
                sid = ref.get("source_id") if isinstance(ref, dict) else None
                source = sources.get(sid) if isinstance(sid, str) else None
                if not source:
                    errors.append(rid + " 引用了不存在的来源")
                    continue
                if source.get("kind") == "book":
                    reviewed = {p for loc in source.get("reviewed_locations", []) for p in loc.get("pdf_pages", [])}
                    used = ref.get("pdf_pages")
                    pages = source.get("pdf_pages")
                    if type(pages) is not int or not isinstance(used, list) or not used or any(
                        type(p) is not int or not 1 <= p <= pages or p not in reviewed for p in used
                    ):
                        errors.append(rid + " 引用页不在实际已读范围内")
            if record.get("status") == "validated":
                proof = record.get("validation_refs", [])
                if not text_list(proof) or not proof or any(
                    pid not in feedback or feedback[pid].get("verified") is not True for pid in proof
                ):
                    errors.append(rid + " 缺少已核验反馈，不能标为 validated")
            if group == "cases":
                method_ids = record.get("method_ids", [])
                if not text_list(method_ids) or any(key not in methods for key in method_ids):
                    errors.append(rid + " 引用了不存在的方法")
                if record.get("case_type") not in {
                    "deployed", "author_report", "counterfactual_rewrite", "writing_exercise", "synthetic", "comparative_field_teardown"
                }:
                    errors.append(rid + " 案例类型无效")
                if not has_text(record.get("analysis")) or not all(
                    text_list(record.get(field)) for field in ("observations", "transfer_limits")
                ):
                    errors.append(rid + " 需要文本分析、观察和适用边界")
                evidence = record.get("outcome_evidence")
                if not isinstance(evidence, dict) or not all(
                    has_text(evidence.get(field)) for field in ("evidence_type", "claim", "verification_status")
                ):
                    errors.append(rid + " 效果证据缺少类型、主张或核验状态")
                elif (
                    record.get("case_type") in {"counterfactual_rewrite", "writing_exercise", "synthetic"}
                    and evidence["verification_status"] == "verified_market_result"
                ):
                    errors.append(rid + " 假设改写/练习不能标为真实市场结果")
    return errors


def search_text(value):
    if isinstance(value, str):
        return " ".join(TOKEN.findall(unicodedata.normalize("NFKC", value).casefold()))
    if isinstance(value, dict):
        value = list(value.values())
    if isinstance(value, list):
        return " ".join(search_text(item) for item in value)
    return ""


def search_fields(record):
    application = record.get("application")
    application = application if isinstance(application, dict) else {}
    fields = {
        3: [record.get(key) for key in ("id", "title", "title_en", "tags", "tags_en", "when_stuck")],
        2: [record.get("rule"), record.get("applies_when"), *(
            application.get(key) for key in ("trigger", "applies_when", "use_when")
        )],
        1: [record.get(key) for key in ("analysis", "observations", "transfer_limits", "limits", "author", "original_title")],
    }
    return {weight: [search_text(value) for value in values] for weight, values in fields.items()}


def infer_learning_origin(record, group, sources_by_id):
    explicit = record.get("learning_origin")
    if isinstance(explicit, str) and explicit in LEARNING_ORIGINS:
        return explicit
    if group == "feedback":
        return "task_feedback"
    if group == "sources":
        kind = record.get("kind")
        if kind == "book":
            return "book_canon"
        if kind == "field_teardown":
            return "co_dissected_teardown"
        return "benchmark_study"
    for ref in record.get("source_refs", []):
        sid = ref.get("source_id") if isinstance(ref, dict) else None
        src = sources_by_id.get(sid) if isinstance(sid, str) else None
        if src:
            s_origin = infer_learning_origin(src, "sources", sources_by_id)
            if s_origin in ("co_dissected_teardown", "book_canon"):
                return s_origin
    return "benchmark_study"


def search_catalog(data, query, kind, limit, origin_filter=None):
    normalized = search_text(query)
    terms = set(normalized.split()) - STOP_WORDS
    if not terms or not 1 <= limit <= 20:
        raise ValueError("需要关键词，limit 范围为 1-20")
    sources_by_id = {s.get("id"): s for s in data.get("sources", []) if isinstance(s, dict) and s.get("id")}
    records = [
        (group, record) for group, record in all_records(data)
        if (kind is None or group == kind)
        and record.get("status") != "retired"
        and (origin_filter is None or infer_learning_origin(record, group, sources_by_id) == origin_filter)
    ]
    # Match authored Chinese keywords inside a question without requiring a tokenizer.
    han_queries = [term for term in terms if HAN.search(term)]
    if han_queries:
        for _, record in records:
            phrases = search_text([record.get("tags"), (record.get("when_stuck") or {}).get("zh")])
            terms.update(
                phrase for phrase in phrases.split()
                if len(phrase) >= 2 and HAN.search(phrase) and any(phrase in q for q in han_queries)
            )

    def match_weight(needle, fields):
        if HAN.search(needle):
            return max((w for w, values in fields.items() if any(needle in v for v in values)), default=0)
        return max((w for w, values in fields.items() if any(f" {needle} " in f" {v} " for v in values)), default=0)

    results = []
    for group, record in records:
        fields = search_fields(record)
        # A term contributes once, at its strongest match. Long notes cannot win by repetition.
        score = sum(match_weight(term, fields) for term in terms)
        if len(normalized.split()) > 1:
            score += 2 * match_weight(normalized, fields)
        if query.strip().casefold() == record["id"].casefold():
            score += 100
        if not score:
            continue
        results.append({
            "group": group,
            "id": record["id"],
            "learning_origin": infer_learning_origin(record, group, sources_by_id),
            "title": record["title"],
            **{key: record[key] for key in ("title_en", "tags_en") if key in record},
            "version": record["version"],
            "status": record.get("status", record.get("reading_status")),
            "score": score,
            "tags": record.get("tags", []),
            "source_refs": record.get("source_refs", []),
            "summary": record.get("rule", record.get("analysis", ""))[:240],
        })
    results.sort(key=lambda row: (-row["score"], row["id"]))
    return {"query": query, "total_matches": len(results), "results": results[:limit]}


def get_records(root, data, ids):
    matches = {key: [] for key in ids}
    for group, record in all_records(data):
        key = record["id"]
        if key in matches:
            matches[key].append((group, record))
    unresolved = [key for key, rows in matches.items() if len(rows) != 1]
    if unresolved:
        raise ValueError("记录不存在或编号重复：" + ", ".join(unresolved))
    results = []
    for key in ids:
        group, original = matches[key][0]
        record = dict(original)
        if group == "cases":
            for field, folder in (("markdown_path", "cases"), ("markdown_path_en", "cases/en")):
                record.pop(field, None)
                if not SAFE_ID.fullmatch(key):
                    continue
                path = (root / folder / f"{key}.md").resolve()
                if path.is_relative_to(root) and path.is_file():
                    record[field] = path.relative_to(root).as_posix()
        results.append({"group": group, "record": record})
    return results[0] if len(ids) == 1 else {"records": results}


def merge_patch(data, patch):
    if not isinstance(patch, dict) or set(patch) != {"base_revision", "reason", "changes"}:
        raise ValueError("补丁需要 base_revision、reason 和 changes 三个字段")
    base = patch["base_revision"]
    if type(base) is not int or base < 1 or not has_text(patch["reason"]):
        raise ValueError("补丁需要有效的引用版本和变更说明")
    if base != data["revision"]:
        raise ValueError(f"补丁基于 r{base}，当前库为 r{data['revision']}。请重读并核对变更。")
    changes = patch["changes"]
    if not isinstance(changes, list) or not changes:
        raise ValueError("补丁至少需要一条变更")

    candidate = deepcopy(data)
    positions = {
        row["id"]: (group, i)
        for group in GROUPS for i, row in enumerate(candidate[group])
    }
    seen, results = set(), []
    for change in changes:
        if not isinstance(change, dict) or set(change) != {"op", "group", "record"}:
            raise ValueError("每条变更需要 op、group 和 record")
        op, group, record = change["op"], change["group"], change["record"]
        if op not in ("add", "update") or group not in GROUPS or not isinstance(record, dict):
            raise ValueError("只接受资料库分组内的 add 或 update 记录")
        key = record.get("id")
        if not isinstance(key, str) or not SAFE_ID.fullmatch(key) or "version" in record:
            raise ValueError("需要有效记录 ID，version 由命令生成")
        if key in seen:
            raise ValueError("同一补丁内记录重复：" + key)
        seen.add(key)
        if op == "add":
            if key in positions:
                raise ValueError("要新增的记录已存在：" + key)
            version = 1
            candidate[group].append({**record, "version": version})
        else:
            if key not in positions or positions[key][0] != group:
                raise ValueError("要更新的记录在指定分组中不存在：" + key)
            i = positions[key][1]
            original = candidate[group][i]
            merged = {**original, **record}
            if merged == original:
                raise ValueError("记录没有实际变更：" + key)
            version = original["version"] + 1
            candidate[group][i] = {**merged, "version": version}
        results.append({"op": op, "group": group, "id": key, "version": version})

    candidate["revision"] = base + 1
    candidate["updated_at"] = date.today().isoformat()
    candidate.setdefault("change_log", []).append({
        "revision": candidate["revision"],
        "date": candidate["updated_at"],
        "reason": patch["reason"],
        "added": [row["id"] for row in results if row["op"] == "add"],
        "updated": [row["id"] for row in results if row["op"] == "update"],
    })
    return candidate, results


@contextmanager
def catalog_lock(path):
    lock = path.with_name(f".{path.name}.lock")
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError(f"资料库已锁定：{lock}") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(f"{os.getpid()}\n")
        yield
    finally:
        lock.unlink()


def atomic_write(path, contents, mode):
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        pending = Path(handle.name)
        try:
            handle.write(contents)
            handle.flush()
            os.fsync(handle.fileno())
            handle.close()
            pending.chmod(mode)
            os.replace(pending, path)
        finally:
            pending.unlink(missing_ok=True)


def apply_catalog_patch(root, catalog, original, data, patch, dry_run, check_files):
    errors = validate(root, data, check_files=False)
    candidate, changes = merge_patch(data, patch) if not errors else (data, [])
    if not errors:
        errors = validate(root, candidate, check_files)
    result = {
        "ok": not errors,
        "applied": False,
        "dry_run": dry_run,
        "library": str(root),
        "catalog_revision": data["revision"],
        "candidate_revision": candidate["revision"],
        "changes": changes,
        "errors": errors,
    }
    if errors or dry_run:
        return result

    contents = (json.dumps(candidate, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    with catalog_lock(catalog):
        if catalog.read_bytes() != original:
            raise ValueError("资料库在检查期间改变。请重读并核对补丁。")
        history = catalog.parent / "history"
        backup = history / f"catalog-r{data['revision']}.json"
        if history.is_symlink() or backup.is_symlink():
            raise ValueError("历史目录和备份必须是库内的真实文件")
        history.mkdir(exist_ok=True)
        mode = stat.S_IMODE(catalog.stat().st_mode)
        if not backup.exists():
            atomic_write(backup, original, mode)
        elif backup.read_bytes() != original:
            raise ValueError(f"已存在不同内容的历史备份：{backup}")
        atomic_write(catalog, contents, mode)
    return {**result, "applied": True, "catalog_revision": candidate["revision"], "backup": str(backup)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", help="资料库根目录，置于子命令之前")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("summary")
    search = subs.add_parser("search")
    search.add_argument("query")
    search.add_argument("--kind", choices=GROUPS)
    search.add_argument("--origin", choices=sorted(LEARNING_ORIGINS))
    search.add_argument("--limit", type=int, default=5)
    get = subs.add_parser("get")
    get.add_argument("ids", nargs="+")
    check = subs.add_parser("validate")
    check.add_argument("--check-files", action="store_true", help="另核对库中保存的书籍原件和指纹")
    apply = subs.add_parser("apply-patch", help="校验并写入已审核的记录补丁")
    apply.add_argument("--file", required=True, type=Path)
    apply.add_argument("--dry-run", action="store_true", help="预览变更和校验结果，不写入资料库")
    apply.add_argument("--check-files", action="store_true", help="同时核对已保存的书籍原件和指纹")
    args = parser.parse_args()
    root, catalog = locate_catalog(args.library)
    original = catalog.read_bytes()
    data = parse_catalog(original)
    sources_by_id = {s.get("id"): s for s in data.get("sources", []) if isinstance(s, dict) and s.get("id")}
    context = {"library": str(root), "catalog_revision": data["revision"]}
    if args.command == "summary":
        by_origin = {}
        for g in GROUPS:
            g_counts = {}
            for item in data[g]:
                orig = infer_learning_origin(item, g, sources_by_id)
                g_counts[orig] = g_counts.get(orig, 0) + 1
            by_origin[g] = g_counts
        emit({**context, "counts": {g: len(data[g]) for g in GROUPS}, "by_learning_origin": by_origin, "sources": [{**{k: s.get(k) for k in ("id", "title", "reading_status", "pdf_pages", "coverage_note", "reviewed_locations")}, "learning_origin": infer_learning_origin(s, "sources", sources_by_id)} for s in data["sources"]]})
    elif args.command == "get":
        emit({**context, **get_records(root, data, args.ids)})
    elif args.command == "search":
        emit({**context, **search_catalog(data, args.query, args.kind, args.limit, getattr(args, "origin", None))})
    elif args.command == "apply-patch":
        patch = json.loads(args.file.expanduser().read_text(encoding="utf-8"))
        result = apply_catalog_patch(root, catalog, original, data, patch, args.dry_run, args.check_files)
        emit(result)
        return 0 if result["ok"] else 1
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
