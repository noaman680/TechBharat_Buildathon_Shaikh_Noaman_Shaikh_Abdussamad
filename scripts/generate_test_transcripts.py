"""
Generate synthetic labeled transcripts for the eval suite — useful for
quickly expanding EVAL_CASES beyond the hand-written fixtures.

Usage: python scripts/generate_test_transcripts.py --count 20
"""
import argparse


def generate(count: int):
    raise NotImplementedError(
        "TODO: prompt an LLM to generate realistic meeting transcripts with "
        "known ground-truth action items/decisions/risks embedded, then write "
        "both the transcript and its label set into backend/tests/eval/test_cases/"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()
    generate(args.count)
