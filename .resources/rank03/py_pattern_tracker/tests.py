from pathlib import Path
import runpy
import sys

candidate = Path(__file__).resolve().parents[3] / "rendu/py_pattern_tracker/py_pattern_tracker.py"
sys.argv = [sys.argv[0], "py_pattern_tracker", str(candidate)]
runpy.run_path(str(Path(__file__).resolve().parents[1] / "tester.py"), run_name="__main__")