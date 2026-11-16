# Copywriting

[简体中文](README.md)

`copywriting-learning` is an AI skill for writing and editing English ads, product pages, marketing emails, and customer replies. It uses your brief and verified facts to find a relevant example, then adapts the writing technique to your audience and channel. It can also analyze campaigns and books and turn real feedback into reusable writing methods.

**v1.1.2** includes **45 cases and exercises with source references** and **24 searchable writing methods**. The new entries cover 18 VeryGoodCopy Micro-Lessons by Eddie Shleyner. The English index explains what to look for in each entry and links to detailed notes in Chinese. [Browse the English case index](copywriting-learning/library/README.en.md)

[Changelog](CHANGELOG.en.md) · [Report a problem or suggest an improvement](https://github.com/XavierCrea/copywriting-learning/issues)

## Getting started

Download **Source code (zip)** from the release page and extract the entire `copywriting-learning` folder. For a local Codex project, put the folder in the project's `.agents/skills/` directory and select the skill from the skill list. [Download the latest release](https://github.com/XavierCrea/copywriting-learning/releases/latest) · [OpenAI installation guide](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

### What to give the skill

1. **The deliverable and where it will appear.** Ask for a product-page headline and supporting line, an ad opener, a sales email, or a customer reply. Include any length, tone, or format requirements.
2. **The reader and the next step.** Tell the skill who will read the copy and what they should understand, decide, or do next.
3. **What you can say with confidence.** Share the selling points, specs, test conditions, draft, or customer message you want to use. Mark any language or figures that need to stay and anything that needs confirmation.

You can give the brief in English or Chinese and request an English draft. A spec sheet, interview notes, or an existing draft gives the skill enough to suggest possible selling points when you're still deciding what to emphasize.

### Try it with a case

These sample briefs use facts from the library. The English drafts show how a technique can be applied to those facts.

**Write a product-page headline**

> Use $copywriting-learning to write a headline and one supporting line for a warehouse manager. Use the Zebra and Saddle Creek workflow where staff scan the item barcode, verify the order, and print the shipping label. Make it clear that the label is printed after the order is verified.

The case shows where the technology fits in the work. In the sample headline, three short verbs put the steps in reading order. [Zebra and Saddle Creek case notes in Chinese](copywriting-learning/library/cases/C-zebra-saddle-creek-workflow-proof.md)

> **Headline**　Scan. Verify. Print.
>
> **Supporting line**　Staff scan the item barcode, verify the order, then print the shipping label.

**Reply to a customer who asks for a specification**

> Use $copywriting-learning to write a short reply based on the scale-weight inquiry case. The customer asks how much the scale itself weighs. The ad lists its capacity, and the scale's weight still needs to be confirmed. Give the customer a clear next step.

The case identifies the specification buyers keep asking for. The phrase `the scale itself` pinpoints what the reply will verify. [Scale-weight inquiry case notes in Chinese](copywriting-learning/library/cases/C-sugarman-scale-buyer-questions.md)

> Thanks for asking. I’ll confirm what the scale itself weighs and send you the figure.

**Analyze a case**

> Use $copywriting-learning to analyze the Rolls-Royce ad. Explain how the clock conveys a quiet cabin and what conditions a writer should check before using this technique for another product.

[Rolls-Royce case notes in Chinese](copywriting-learning/library/cases/C-rolls-royce-specific-detail.md)

## How the skill uses cases

1. **Retrieve.** Turn the reader's question or the draft's weak point into search terms. Open a case that tackles the same writing problem.
2. **Reuse.** Pick a specific move that fits the new brief, such as addressing installation concerns early. Bring in a second case when it helps solve another problem, such as tightening a headline.
3. **Revise.** Write from the facts in the new brief. Keep any measurement conditions and limits in the copy. Make customer replies easy to answer and ad copy specific, concise, and easy to say.
4. **Retain.** When you have actual feedback, you can ask the skill to record what changed, which technique it used, and what the feedback supports.

This workflow draws on case-based reasoning. [Aamodt and Plaza's paper](https://www.iiia.csic.es/~enric/papers/Aamodt_1994_Case.pdf)

The writing guide explains how to choose which benefit to emphasize, use a detail or a short scene, shape sentence rhythm, and cut words while preserving meaning. [Writing guide in Chinese](copywriting-learning/references/writing.md)

## Learning from a case

A case note identifies the reader, how the original copy is organized, which wording may shape a decision, and the conditions under which the technique can be reused. You can trace observations, interpretations, and reported results to a source and page or section. For a new campaign or book, share a link or source file the skill can open.

When a case involves a current trend, check when the event happened, when the material appeared, and who saw it. For a live brief, record editorial feedback, approval for use, and measured outcomes with the evidence that supports each.

## Four cases to start with

| Case | What to study | Source |
| --- | --- | --- |
| [Rolls-Royce advertising](copywriting-learning/library/cases/C-rolls-royce-specific-detail.md) | Make an abstract quality tangible through one detail the reader can imagine hearing. | David Ogilvy, *Ogilvy on Advertising*, 2013 Chinese edition, printed pp. 6–7 and 240. |
| [Magic Stat thermostat](copywriting-learning/library/cases/C-sugarman-magicstat-objection-sequence.md) | Address installation and wiring concerns, then explain programming through everyday routines. | Joseph Sugarman, *The Adweek Copywriting Handbook*, 2011 Chinese edition, printed pp. 212–216. |
| [Zebra and Saddle Creek](copywriting-learning/library/cases/C-zebra-saddle-creek-workflow-proof.md) | Explain a device through the task it supports. The vendor reports results for the wider solution. | [Zebra customer case, PDF pp. 2–3](https://www.zebra.com/content/dam/zebra_dam/en/success-story/logistics-success-story-saddle-creek-end-user-en-us.pdf) |
| [Cookie availability experiment](copywriting-learning/library/cases/C-cialdini-cookie-availability.md) | Use product facts to explain why an offer fits and actual availability to explain why timing matters. | Robert B. Cialdini, *Influence*, 2006 Chinese edition, printed pp. 323–324, 327–328, and 334. |

## How it works

| File | Purpose |
| --- | --- |
| [SKILL.md](copywriting-learning/SKILL.md) | Defines when the skill is used and how it drafts, analyzes cases, and learns from feedback. |
| [references/](copywriting-learning/references) | Contains the writing, research, and record-keeping instructions the agent reads for the task. |
| [library/catalog.json](copywriting-learning/library/catalog.json) | Stores sources, cases, methods, and feedback as searchable records. |
| [scripts/library.py](copywriting-learning/scripts/library.py) | Searches case records, opens a record by ID, and validates the library. |

With Python 3.9 or above, run these commands from the `copywriting-learning` folder. Search works with indexed terms such as the brand or model name below. You can also find a case in the English index and use its ID directly.

```bash
python3 scripts/library.py search "MagicStat" --kind cases --limit 3
python3 scripts/library.py get C-sugarman-magicstat-objection-sequence
python3 scripts/library.py validate
```

To use a different library, pass `--library "/path/to/your-library"` before a subcommand or set `COPYWRITING_LIBRARY_ROOT`. Use `validate --check-files` when the library includes locally stored source files.

[Maintainer guide](MAINTAINING.en.md)
