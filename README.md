
# Copywriting 文案研究与案例学习

`copywriting-learning` 是一套 AI 文案技能。它根据产品事实、读者需求和发布场景撰写或改写广告、产品卖点、详情页、营销邮件与品牌文案。它也能拆解广告、提炼书中的写法，并把实际反馈整理成以后可以检索的记录。

**当前版本 v0.1.1。** 公开资料包含 **27 个有出处的案例和 24 条写作方法**。读者可以直接浏览案例页，技能可以按任务检索案例与方法。 [浏览全部案例](copywriting-learning/library/README.md)

[查看更新记录](CHANGELOG.md) · [维护方式](MAINTAINING.md) · [反馈问题或建议](https://github.com/XavierCrea/copywriting/issues)

当你手里有一份规格表、一堆访谈或一版旧稿时，可以先让技能回答三个问题。读者要做什么判断？哪条产品事实能帮他判断？怎样写，他在这个渠道里最容易理解？

## 写作方法

把客户原话、旧稿或已确认的产品资料交给技能，说明写给谁、发在哪里、希望读者接下来做什么。技能根据你卡住的地方，用案例推理把已有案例用到新稿。 [案例推理的方法出处](https://www.iiia.csic.es/~enric/papers/Aamodt_1994_Case.pdf)

1. **检索。** 把「客户一直担心装不上」这类描述转成「安装、适配、顾虑」等检索词，打开处理同类问题的案例。
2. **借用。** 从主案例提取一个可用的写作动作，如先回答安装条件，再写使用价值。需要再处理另一项难题时，可以借第二例打磨标题或精简文字。
3. **修订。** 用自己的产品事实写成新稿，保留参数和适用条件。客户回复关注如何接住顾虑和推进下一步，广告关注利益说得是否具体、文字是否精炼准确。
4. **留存。** 有实际反馈时，可以请技能记录借了哪种写法、哪句话改了、反馈能说明什么。

下面两条用假设任务展示怎样调用案例。

### 从客户原话写到回复

> 用文案技能写一条客户回复。客户问「这款 BMS 能接我们的旧控制器吗？」我有这款 BMS 的 CAN 报文样例，客户还没提供控制器型号。

技能可以借用 Magic Stat 恒温器先回应安装顾虑的顺序，把适配判断放在卖点前。 [Magic Stat 案例](copywriting-learning/library/cases/C-sugarman-magicstat-objection-sequence.md)

> 您方便发一下旧控制器的型号吗？如果手头有 CAN 协议资料，也可以一起发来。我把这款 BMS 的报文样例发您，我们先对照一下。

### 从旧广告写到新标题

> 用文案技能把「强力磁吸，高效检修」改成一句有画面的广告标题。已确认工作灯能吸在钢制机柜上，检修时可以腾出双手。

技能可以借劳斯莱斯广告找一个读者能想象的事实，再借体重秤编辑练习删去泛词，留下「钢柜」这个条件和「腾出双手」的价值。 [劳斯莱斯案例](copywriting-learning/library/cases/C-rolls-royce-specific-detail.md) · [体重秤编辑练习](copywriting-learning/library/cases/C-scale-editing-exercise.md)

> 灯吸在钢柜上，双手留给检修。

## 怎样从案例学习

读到一则案例时，记录它写给谁、原文怎样展开、哪个表达可能影响读者的判断，以及换到什么任务时可以借用。同一张案例卡保留出处、实际阅读的页码或段落、原文观察、分析和已知结果。作者回顾、品牌方自述、实验结果与实际客户反馈各自注明来源。

需要借鉴近期热点时，先核对事件时间、文章发布时间与原始出处，再判断这个话题是否和目标读者的处境或产品用途有关。阅读量、询盘和成交按各自能说明的问题记录。

用到真实任务后，可以补记采用的写法与收到的反馈。编辑认可记录为文字反馈，交付验收记录为使用反馈，市场结果需要对应指标、周期和出处。依据这些记录修订方法时，保留旧版和变更原因。

## 从这四例开始

| 案例 | 能学到的写法 | 出处 |
| --- | --- | --- |
| [劳斯莱斯广告](copywriting-learning/library/cases/C-rolls-royce-specific-detail.md) | 用一个容易想象的听觉细节表达车厢的安静，再补上来源与购买时会关心的细节。适合练习从产品研究里找标题。 | 大卫·奥格威《奥格威谈广告（全彩版）》，机械工业出版社，2013 年版，印刷第 6–7、240 页。 |
| [Magic Stat 恒温器](copywriting-learning/library/cases/C-sugarman-magicstat-objection-sequence.md) | 把安装和接线顾虑提到前面，再用起床、离家和睡觉等场景解释定时功能。适合练习长文案的信息顺序。 | 约瑟夫·休格曼《文案训练手册》，中信出版社，2011 年版，印刷第 212–216 页。 |
| [Zebra × Saddle Creek](copywriting-learning/library/cases/C-zebra-saddle-creek-workflow-proof.md) | 把设备放回扫码、核单、打印标签的工作流程，让采购者理解它接在哪一步。改善属于供应商案例中的方案级报告。 | [Zebra 官方案例，PDF 第 2–3 页](https://www.zebra.com/content/dam/zebra_dam/en/success-story/logistics-success-story-saddle-creek-end-user-en-us.pdf) |
| [曲奇供给实验](copywriting-learning/library/cases/C-cialdini-cookie-availability.md) | 用产品依据解释「为什么适合」，用真实供给情况解释「为什么现在考虑」。书中转述的是参与者对曲奇的评价和获得意愿。 | 罗伯特·B. 西奥迪尼《影响力》，中国人民大学出版社，2006 年版，印刷第 323–324、327–328、334 页。 |

### 一段改写示范

以 Zebra 案例记载的发货流程为例。原稿是为了展示改写差异而拟写的句子。

> **初稿**　帮助仓库实现高效智能的标签打印。
>
> **改写**　工作人员在拣货工位扫描商品、核对订单，然后打印发货标签。

这一版把注意力放到主管能核对的工作步骤。若要进一步写每单节省多少时间，可以用该工位实际测得的数据补充。流程出处见 [Zebra 官方案例第 3 页](https://www.zebra.com/content/dam/zebra_dam/en/success-story/logistics-success-story-saddle-creek-end-user-en-us.pdf#page=3)。

## 开始使用

1. 下载后保留整个 [`copywriting-learning` 文件夹](copywriting-learning)。在本地 Codex 项目中，可以放到项目的 `.agents/skills/` 目录，再从技能列表选择它。安装方式见 [OpenAI 技能文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。
2. 在任务中提供产品资料、读者、发布位置与目标。检索默认使用技能内的案例库。要学习新案例或核对书中原句，提供可访问的原材料链接或文件。

**写一段文案**

> 用文案研究与案例学习技能，根据下面的已确认资料，为仓库主管写一段英文产品文案。讲清设备用在哪一步、操作有什么变化。保留资料中的参数和适用条件。

**拆解一则案例**

> 用文案研究与案例学习技能，阅读这则广告及我附的背景材料。告诉我它怎样组织信息、哪种写法可以用到我的产品页、有哪些成立条件。把出处和实际阅读范围写进案例卡。

## 实现方式

| 文件 | 用途 |
| --- | --- |
| [`SKILL.md`](copywriting-learning/SKILL.md) | 告诉 AI 何时使用技能，以及怎样完成写作、案例拆解和后续更新。 |
| [`references/`](copywriting-learning/references) | 保存写作流程、学习更新规则、案例来源指引和知识记录格式，按任务读取。 |
| [`library/catalog.json`](copywriting-learning/library/catalog.json) | 把资料出处、方法、案例与反馈保存成可按主题检索的记录。 |
| [`scripts/library.py`](copywriting-learning/scripts/library.py) | 用 Python 做关键词检索、读取单条记录、检查资料格式和引用。脚本只读，写作和经授权的案例更新由 AI 按工作流程完成。 |

如需手动试用检索，可在 `copywriting-learning` 文件夹内用 Python 3.9 或更高版本运行下面的命令。第一个命令查找和安装顾虑有关的案例，第二个读取一张完整案例卡，第三个检查资料库格式与引用关系。

```bash
python3 scripts/library.py search "安装 顾虑" --kind cases --limit 3
python3 scripts/library.py get C-sugarman-magicstat-objection-sequence
python3 scripts/library.py validate
```

也可以在 `search`、`get` 等子命令前加 `--library "/path/to/your-library"`，或设置 `COPYWRITING_LIBRARY_ROOT`，使用自己的资料库。公开库提供书目、页码和公开链接。需要核对本地库保存的书籍原件时，可使用 `validate --check-files`。
