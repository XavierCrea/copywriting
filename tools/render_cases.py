#!/usr/bin/env python3
"""Render the case pages that readers open on GitHub."""

import argparse
import json
from pathlib import Path
import re

from check_translations import check_translations


LIBRARY = Path(__file__).resolve().parents[1] / "copywriting-learning" / "library"
CASE_KINDS = {
    "author_report": "原广告或案例记录及作者、发布方的叙述",
    "deployed": "已发布案例",
    "counterfactual_rewrite": "原广告点评与假设改写",
    "writing_exercise": "写作练习",
    "synthetic": "模拟示例",
}
EVIDENCE_STATES = {
    "unknown": "效果未知",
    "not_independently_verified": "效果由原来源报告或转述",
    "verified_market_result": "有已核验的市场结果",
}


def page_span(pages):
    ranges = []
    for page in sorted(set(pages)):
        if ranges and page == ranges[-1][1] + 1:
            ranges[-1][1] = page
        else:
            ranges.append([page, page])
    return "、".join(str(first) if first == last else f"{first}–{last}" for first, last in ranges)


def citation(ref, source):
    pdf = page_span(ref.get("pdf_pages", []))
    if source["kind"] == "book":
        publication = "，".join(
            value for value in (f"{source.get('author', '')}《{source['title']}》", source.get("publisher"), source.get("edition")) if value
        )
        printed = page_span(ref.get("printed_pages", []))
        if printed:
            publication += f"，印刷第 {printed} 页"
        if pdf:
            publication += f"（原件 PDF 第 {pdf} 页）"
        return publication + "。"

    details = [source.get("publisher"), source.get("document_date"), f"PDF 第 {pdf} 页" if pdf else None]
    label = "，".join(value for value in details if value)
    title = source["title"]
    if source.get("url"):
        title = f"[{title}]({source['url']})"
    return f"{label}。{title}" if label else title


def add_list(lines, heading, items, marker="-"):
    if items:
        lines.extend(["", f"## {heading}", ""])
        lines.extend(f"{marker} {item}" for item in items)


def render_case(case, sources, methods):
    lines = [f"# {case['title']}", "", f"[返回案例库](../README.md) · [English](en/{case['id']}.md) · {CASE_KINDS[case['case_type']]}", ""]
    context = case.get("brief") or case.get("context") or {}
    for label, value in (
        ("背景", context.get("situation") or context.get("brand_product")),
        ("读者", context.get("audience")),
        ("任务", context.get("task") or context.get("communication_goal")),
        ("渠道", context.get("channel")),
    ):
        if value:
            lines.append(f"- **{label}**　{value}")
    add_list(lines, "原材料里看到什么", case["observations"])
    lines.extend(["", "## 这段写法怎样起作用", "", case["analysis"]])
    application = case.get("application", {})
    add_list(lines, "可借用的写作步骤", application.get("steps"), "1.")
    if application.get("expression_blueprint"):
        lines.extend(["", application["expression_blueprint"]])
    example = application.get("example", {})
    if example.get("type") == "hypothetical":
        quote = [f"> {line}" for line in example["text"].splitlines()]
        lines.extend(["", "## 自拟英文练习", "", *quote, "", example["note"]])
    add_list(lines, "落稿后的检查", application.get("checks"))
    uses = application.get("applies_when") or application.get("use_when") or application.get("trigger") or case.get("applies_when")
    add_list(lines, "适用的任务", [uses] if isinstance(uses, str) else uses)
    add_list(lines, "迁移时注意的条件", case["transfer_limits"])
    outcome = case["outcome_evidence"]
    lines.extend(["", "## 已知效果与依据", "", outcome["claim"]])
    state = EVIDENCE_STATES.get(outcome["verification_status"])
    if state:
        lines.extend(["", f"效果记录为「{state}」。"])
    add_list(lines, "出处", [citation(ref, sources[ref["source_id"]]) for ref in case["source_refs"]])
    if case.get("method_ids"):
        titles = "、".join(methods[key]["title"] for key in case["method_ids"])
        lines.extend(["", f"关联写作方法包括{titles}。"])
    lines.extend(["", f"案例编号 `{case['id']}`，记录版本 {case['version']}。"])
    return "\n".join(lines).rstrip() + "\n"


def render_index(cases, sources):
    lines = [
        "# 文案案例库",
        "",
        f"这里有 {len(cases)} 个案例和练习，每张卡提供原文观察、解读、可借用的步骤、适用边界和来源。技能使用同目录下的资料索引检索案例和关联方法。",
        "",
        "[返回项目首页](../../README.zh-CN.md) · [English index](README.en.md) · [查看可检索的资料库](catalog.json)",
    ]
    groups = {}
    for source_id, source in sources.items():
        name = source.get("series") or source.get("short_title") or source["title"]
        key = source.get("series") or source_id
        groups.setdefault(key, (name, []))
    for case in cases:
        source_id = case["source_refs"][0]["source_id"]
        key = sources[source_id].get("series") or source_id
        groups[key][1].append(case)
    for name, group in groups.values():
        if group:
            lines.extend(["", f"## {name}（{len(group)} 例）", ""])
            lines.extend(f"- [{case['title']}](cases/{case['id']}.md)" for case in group)
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="核对已生成的网页和资料库是否一致")
    args = parser.parse_args()
    data = json.loads((LIBRARY / "catalog.json").read_text(encoding="utf-8"))
    sources = {source["id"]: source for source in data["sources"]}
    methods = {method["id"]: method for method in data["methods"]}
    cases = data["cases"]
    generated = {LIBRARY / "README.md": render_index(cases, sources)}
    for case in cases:
        if not re.fullmatch(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", case["id"]):
            raise ValueError(f"案例编号不适合作为文件名：{case['id']}")
        generated[LIBRARY / "cases" / f"{case['id']}.md"] = render_case(case, sources, methods)

    if args.check:
        if check_translations(LIBRARY):
            return 1
        stale = [path for path, content in generated.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        stale += sorted(set((LIBRARY / "cases").glob("*.md")) - generated.keys())
        for path in stale:
            print(f"需核对：{path.relative_to(LIBRARY)}")
        if stale:
            return 1
    else:
        (LIBRARY / "cases").mkdir(exist_ok=True)
        for path, content in generated.items():
            path.write_text(content, encoding="utf-8")
    print(f"案例目录及 {len(cases)} 个案例页已核对。" if args.check else f"已生成案例目录及 {len(cases)} 个案例页。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
