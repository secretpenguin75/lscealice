import sys
from pathlib import Path
import os


def resolve_path(path: str) -> str:
    origin = (
        Path(sys._MEIPASS)  # type: ignore
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
        else Path(__file__).parent
    )

    return os.path.abspath(Path(origin, path))
