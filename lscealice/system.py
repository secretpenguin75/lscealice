import sys
from pathlib import Path
import os

def resolve_path(path) -> str:
    if getattr(sys, 'frozen', False):
        return os.path.abspath(Path(sys._MEIPASS, path))
    return os.path.abspath(Path(Path(__file__).parent, path))
