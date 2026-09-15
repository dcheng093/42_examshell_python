from pathlib import Path
import runpy
import sys

candidate = Path(__file__).resolve().parents[3] / "rendu/mirror_matrix_vertical/mirror_matrix_vertical.py"
sys.argv = [sys.argv[0], "mirror_matrix_vertical", str(candidate)]
runpy.run_path(str(Path(__file__).resolve().parents[1] / "tester.py"), run_name="__main__")