# 如何维护 Copywriting

[English](MAINTAINING.en.md)

本项目按版本发布。想法或反馈可以先记在 GitHub Issues。准备修改时，新建一个分支，按具体任务试用。确认写法、证据和交付符合预期后，再通过 Pull Request 合并到 `main`。这样每次更新的差异都能单独查看。 [项目反馈](https://github.com/XavierCrea/copywriting-learning/issues)

## 改哪里

| 改动 | 文件 |
| --- | --- |
| 改技能的适用范围、入口或整体流程 | [SKILL.md](copywriting-learning/SKILL.md) |
| 改选案例、写稿、校对或归档的详细要求 | [references/](copywriting-learning/references) |
| 新增或修订来源、写作方法、案例和反馈 | [catalog.json](copywriting-learning/library/catalog.json) |

案例和方法应保留已有编号。修订一条记录时增加它的 `version`，库更新时增加 `revision`，写清来源、适用条件和证据范围。完整约定见[知识记录格式](copywriting-learning/references/knowledge-contract.md)。

## 从资料库更新网页

中文案例页和目录都从同一份资料库生成。改好 `catalog.json` 后，在仓库根目录运行下面的命令。

```bash
python3 copywriting-learning/scripts/library.py validate
python3 tools/render_cases.py
python3 tools/render_cases.py --check
```

提交前看一遍改动，试检索一个受影响的关键词并打开相应的案例链接。新增或修订案例时，同步更新英文索引的题名、用法与链接。有重要能力变化时，更新中英文首页。 [英文案例索引](copywriting-learning/library/README.en.md)

## 发下一版

按改动范围选版本号。比如小修订可用 `v0.1.2`，加入一组新能力可用 `v0.2.0`。更新技能版本、中英文首页和更新记录，并用 Git 标签标记对应提交。版本标签可以用来下载当时的文件，方便比较或恢复。需要发布带说明的下载页时，可在这个标签上创建 GitHub Release。 [中文更新记录](CHANGELOG.md) · [英文更新记录](CHANGELOG.en.md) · [GitHub 版本发布说明](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
