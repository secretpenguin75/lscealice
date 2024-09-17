import sys
from pathlib import Path
import os


def resolve_path(path: str) -> str:
    """
    Examples
    --------
    >>> from pathlib import Path
    >>> path = resolve_path("icon/lapin.png")
    >>> Path(path).stat().st_size
    83426

    """
    origin = (
        Path(sys._MEIPASS)  # type: ignore
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
        else Path(__file__).parent
    )

    return os.path.abspath(Path(origin, path))
