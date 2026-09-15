from pathlib import Path
import runpy
import sys

candidate = Path(__file__).resolve().parents[3] / "rendu/brackets/brackets.py"
sys.argv = [sys.argv[0], "brackets", str(candidate)]
runpy.run_path(str(Path(__file__).resolve().parents[1] / "tester.py"), run_name="__main__")