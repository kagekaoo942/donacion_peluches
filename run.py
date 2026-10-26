import os
import runpy
from pathlib import Path


PROJECT_DIR = (
    Path(__file__).resolve().parent
    / "certificacion_skillnest_donacion_peluches_Martin_acevedo_2026_10_26"
)

os.chdir(PROJECT_DIR)
runpy.run_path(str(PROJECT_DIR / "run.py"), run_name="__main__")
