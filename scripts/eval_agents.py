"""
CLI entrypoint for the evaluation framework. Fails CI if scores drop below
`--threshold`. See backend/tests/eval/evaluate.py for the implementation.

Usage: python scripts/eval_agents.py --threshold 0.80
"""
import argparse
import asyncio
import sys

sys.path.insert(0, "backend")

from tests.eval.evaluate import EVAL_CASES, evaluate_extraction_quality  # noqa: E402


async def main(threshold: float):
    report = await evaluate_extraction_quality(EVAL_CASES)
    print(f"Precision: {report.precision:.2f}  Recall: {report.recall:.2f}  F1: {report.f1:.2f}")
    if report.f1 < threshold:
        print(f"FAILED: F1 {report.f1:.2f} below threshold {threshold}")
        sys.exit(1)
    print("PASSED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=0.80)
    args = parser.parse_args()
    asyncio.run(main(args.threshold))
