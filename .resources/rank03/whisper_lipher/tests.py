from pathlib import Path
import runpy
import sys

candidate = Path(__file__).resolve().parents[3] / "rendu/whisper_lipher/whisper_lipher.py"
sys.argv = [sys.argv[0], "whisper_lipher", str(candidate)]
runpy.run_path(str(Path(__file__).resolve().parents[1] / "tester.py"), run_name="__main__")