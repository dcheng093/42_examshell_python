from pathlib import Path
import runpy
import sys

candidate = Path(__file__).resolve().parents[3] / "rendu/merge_and_sort_desc/merge_and_sort_desc.py"
sys.argv = [sys.argv[0], "merge_and_sort_desc", str(candidate)]
runpy.run_path(str(Path(__file__).resolve().parents[1] / "tester.py"), run_name="__main__")