from pathlib import Path

from .system import resolve_path


class TestResolvePath:
    def test_icon(self):
        path = resolve_path("icon/lapin.png")

        result = Path(path).stat()

        assert result.st_size == 83426
