# Maintaining Copywriting

[简体中文](MAINTAINING.md)

Start from a branch and try the change on a realistic writing task. Use a pull request to review the copy, supporting evidence, and deliverable before merging into `main`. [Open an issue or share feedback](https://github.com/XavierCrea/copywriting/issues)

## Where to make changes

| To change | Edit |
| --- | --- |
| When the skill is used or how it works overall | [SKILL.md](copywriting-learning/SKILL.md) |
| How the skill finds cases, drafts, checks, and records feedback | [references/](copywriting-learning/references) |
| Sources, methods, cases, and feedback | [catalog.json](copywriting-learning/library/catalog.json) |
| English case titles and ways to use them | [English case index](copywriting-learning/library/README.en.md) |

Keep case and method IDs stable. When revising a record, increment its `version`. Increment the catalog's `revision` when updating the library. Record the source, conditions of use, and scope of the evidence. [Record format in Chinese](copywriting-learning/references/knowledge-contract.md)

## Update the case pages

The Chinese case pages and index are generated from the catalog. After editing the catalog, run the following commands from the repository root.

```bash
python3 copywriting-learning/scripts/library.py validate
python3 tools/render_cases.py
python3 tools/render_cases.py --check
```

Update the English index's title, writing technique, and link when its case changes. Try a search that should find the affected case and open the links. Update both versions of the homepage when the skill's capabilities change.

## Publish the next version

Choose a version that matches the change. A small revision could be `v0.1.2`, and a substantial addition could be `v0.2.0`. Update the skill version, both homepages, and both changelogs. Tag the corresponding commit so readers can download a particular version. A GitHub Release adds a download page with release notes. [English changelog](CHANGELOG.en.md) · [Chinese changelog](CHANGELOG.md) · [GitHub release documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
