"""Run the evaluation suite against golden test cases."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from tests.eval.evaluate import run_evaluation

if __name__ == "__main__":
    run_evaluation()
