from pathlib import Path
import runpy
import sys

candidate = Path(__file__).resolve().parents[3] / "rendu/py_echo_validator/py_echo_validator.py"
sys.argv = [sys.argv[0], "py_echo_validator", str(candidate)]
runpy.run_path(str(Path(__file__).resolve().parents[1] / "tester.py"), run_name="__main__")