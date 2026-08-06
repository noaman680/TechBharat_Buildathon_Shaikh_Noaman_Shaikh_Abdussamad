"""
Evaluation harness for extraction quality against a labeled ground-truth
dataset. See docs/BLUEPRINT.md §21 for target metrics.

Run via: python scripts/eval_agents.py --threshold 0.80
"""
from dataclasses import dataclass
from typing import List


# Example ground-truth test cases. Add real transcripts under
# tests/eval/test_cases/ and reference them here.
EVAL_CASES = [
    {
        "transcript": "priya_api_docs.txt",
        "expected_items": [
            {
                "title": "Prepare API documentation",
                "owner": "priya@company.com",
                "due_date": "2025-08-29",
                "priority": "high",
                "confidence_min": 0.90,
            }
        ],
        "expected_decisions": 2,
        "expected_risks": 1,
    },
    # ... add 50+ test cases covering edge cases
]


@dataclass
class EvalReport:
    precision: float
    recall: float
    f1: float


async def run_extraction_pipeline(transcript_filename: str):
    raise NotImplementedError("TODO: run the ingestion->extraction agents against a fixture file")


def find_matching_item(extracted: list, expected: dict):
    raise NotImplementedError("TODO: match on title/owner/due_date similarity")


def find_matching_expected(item: dict, expected_items: list):
    raise NotImplementedError("TODO: inverse of find_matching_item")


async def evaluate_extraction_quality(test_cases: List[dict]) -> EvalReport:
    results = {"tp": 0, "fp": 0, "fn": 0}

    for case in test_cases:
        extracted = await run_extraction_pipeline(case["transcript"])

        for expected in case["expected_items"]:
            match = find_matching_item(extracted, expected)
            if match:
                results["tp"] += 1
                assert match["owner_email"] == expected["owner"]
                assert match["due_date_resolved"] == expected["due_date"]
            else:
                results["fn"] += 1

        for item in extracted:
            if not find_matching_expected(item, case["expected_items"]):
                results["fp"] += 1

    precision = results["tp"] / max(results["tp"] + results["fp"], 1)
    recall = results["tp"] / max(results["tp"] + results["fn"], 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)

    return EvalReport(precision=precision, recall=recall, f1=f1)
