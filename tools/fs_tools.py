import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FsTools:
    """Local filesystem helpers scoped to a working directory."""

    def __init__(self, workdir: str = ".") -> None:
        self.workdir = Path(workdir)

    def _abs(self, path: str) -> Path:
        return self.workdir / path

    def read(self, path: str) -> str:
        """Read and return the content of a file."""
        abs_path = self._abs(path)
        if not abs_path.exists():
            raise FileNotFoundError(f"File not found: {abs_path}")
        return abs_path.read_text(encoding="utf-8")

    def write(self, path: str, content: str) -> None:
        """Write *content* to *path*, creating parent directories as needed."""
        abs_path = self._abs(path)
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text(content, encoding="utf-8")
        logger.debug("Wrote %s (%d bytes)", abs_path, len(content))

    def delete(self, path: str) -> None:
        """Delete a file if it exists."""
        abs_path = self._abs(path)
        abs_path.unlink(missing_ok=True)
        logger.debug("Deleted %s", abs_path)

    def exists(self, path: str) -> bool:
        """Return True if the path exists under workdir."""
        return self._abs(path).exists()

    def list(self, directory: str = "") -> list[str]:
        """Return a sorted list of relative file paths under *directory*."""
        base = self._abs(directory) if directory else self.workdir
        paths = []
        for root, _, files in os.walk(base):
            for fname in files:
                abs_file = Path(root) / fname
                rel = abs_file.relative_to(self.workdir)
                paths.append(str(rel).replace("\\", "/"))
        return sorted(paths)
