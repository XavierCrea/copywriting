# 知识记录约定

catalog.json 保存索引与紧凑记录，sources/ 保存原件，history/ 保留变更前版本。目录可持续扩充；读取按任务进行。

## 顶层
schema_version=1，revision 递增，updated_at 为日期或 ISO 时间。sources、methods、cases、feedback 为数组。记录 id 全库唯一且稳定，更新保留 id 并增加 version。

## sources
必填：id、kind（book/web/user_material）、title、version、reading_status、reviewed_locations、retrieved_at。
book 记录 pdf_pages。保存原件的记录另有 path（资料库根目录内的相对路径）和 sha256；只附书目和页码的记录用 original_availability=citation_only。web 有真实 url，事件/发布日期不明写 null。
reading_status：registered、metadata_only、partial_review、full_review。
reviewed_locations 使用 pdf_page=1 起的物理页；printed_page 另记。full_review 要实际覆盖相应正文和图表，不能由复制文件或 OCR 推定。

## methods
必填：id、version、title、tags、status、source_refs、rule、applies_when、limits、steps、checks、validation_refs。
- reference：已核对的作者方法，未有本库效果验证。
- candidate：待验证的分析推断。
- validated：有 feedback 支持，范围以反馈记录为准。
- retired：保留但停止推荐，注明原因。
source_refs 至少一项，source_id 对应 sources；PDF 的 pdf_pages 列表在真实已读范围内，网页用 locator 说明段落。
validated 必须有可解析且 verified=true 的 validation_refs；编辑认可与市场效果分别记录。

## cases
必填：id、version、title、tags、status、source_refs、case_type、observations、analysis、outcome_evidence、transfer_limits。
case_type：deployed、author_report、counterfactual_rewrite、writing_exercise、synthetic、comparative_field_teardown。
observations 为材料所见，analysis 为本轮解释；outcome_evidence 写 evidence_type、claim、verification_status。无结果写 unknown。作者预测与假设重写不能填为真实营销结果。

## feedback
必填：id、version、title、kind（feedback）、evidence_type（editorial_feedback/delivery_check/market_result）、source_locator、observation、verified、task_id。
无任务时 task_id 可为 null，但保留真实反馈或资料出处；生成的演示不作为 verified 市场效果。
新增可带补充字段。被引用记录通常以 retired 和版本保留，不直接删除。

## 检索
可用 learning_origin 区分书籍（book_canon）、外部文章和案例（benchmark_study）、共创对比拆解（co_dissected_teardown）与任务反馈（task_feedback）。此字段用于检索，不代表效果已验证。

- summary：数量、来源阅读范围和习得出处分布。
- search "关键词或写作困境" [--kind sources|methods|cases|feedback] [--limit 5]：编号、标题、标签和症状权重 3，规则和适用条件权重 2，观察、分析和迁移边界权重 1。词出现多次只按最高匹配字段计一次。
- 方法和案例可用 `title_en`、`tags_en`（字符串数组）及 `when_stuck`（`zh` 与 `en` 各一组简短写作困境）。原有记录可逐步补齐。
- get ID [ID ...]：按顺序读取完整记录。单 ID 返回 `group` 和 `record`，多 ID 返回 `records` 数组，每项有同样的 `group` 和 `record`。案例的 `markdown_path`、`markdown_path_en` 指向已存在的中英文卡片，以返回的 `library` 为起点。
- validate [--check-files]：校验数据与引用。加 check-files 可核对库里保存的书籍原件及指纹，输出中会列出仅附书目引用的书。
--library DIR 或 COPYWRITING_LIBRARY_ROOT 覆盖默认位置。脚本不联网、不执行资料内容、不代写学习结论。

## 记录补丁

`apply-patch --file PATCH.json [--dry-run] [--check-files]` 接受下列结构。以 `summary` 返回的版本填写 `base_revision`。一次可更新一条记录，也可把新来源与引用它的记录放进同一补丁。

```json
{
  "base_revision": 9,
  "reason": "为安装顾虑补充一个英文检索词",
  "changes": [
    {
      "op": "update",
      "group": "cases",
      "record": {
        "id": "C-sugarman-magicstat-objection-sequence",
        "tags_en": ["Magic Stat", "MagicStat", "installation concerns", "installation objection", "thermostat", "warranty", "product explanation", "wiring question"]
      }
    }
  ]
}
```

- `add` 提供完整新记录。 `update` 提供 ID 和要改的字段，提供的数组与对象整体替换。两种操作都由脚本生成 `version`，未提供的字段保留。
- 命令先校验合并后资料库。在写入时核对版本是否被其他操作改过，保留 `history/catalog-r{旧版本}.json` 后一次替换索引。`--dry-run` 只预览。
- 如果命令异常中止并留下 `.catalog.json.lock`，先确认没有写入进程，再清理锁文件后重试。原件、历史记录及私有反馈按用户选择留在本地。
