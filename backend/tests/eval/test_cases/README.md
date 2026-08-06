# Ground-truth test cases

Place labeled transcript fixtures here (e.g. `priya_api_docs.txt`) and add a
matching entry to `EVAL_CASES` in `../evaluate.py`.

## Target metrics (docs/BLUEPRINT.md §21)

| Metric | Target |
|---|---|
| Action Item Recall | ≥ 80% |
| Action Item Precision | ≥ 75% |
| Owner Attribution Accuracy | ≥ 85% |
| Date Resolution Accuracy | ≥ 90% |
| End-to-End Latency (45min meeting) | < 5 min |
| Duplicate Task Creation | 0 |
| Unapproved External Actions | 0 |
