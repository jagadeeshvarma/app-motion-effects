"""GA02 metadata-only preflight for submitted trees; never follow submitted links."""
from pathlib import Path
import os
import stat


class UnsafeSubmittedTree(ValueError):
    pass


def preflight_workspace(workspace):
    """Reject links/special files before legacy graders enumerate or read content.

    Check the entire submitted tree, including normally ignored build/config paths.
    A link is rejected even when broken or pointing inside the tree. This is an
    infrastructure boundary, not an extra UI assertion or a source repair.
    """
    root = Path(workspace).absolute()
    counts = {"regular_files": 0, "directories": 0}

    def visit(path, relative):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise UnsafeSubmittedTree(f"Submitted symlink is not allowed: {relative}")
        if stat.S_ISDIR(mode):
            counts["directories"] += 1
            with os.scandir(path) as entries:
                names = sorted(entry.name for entry in entries)
            for name in names:
                visit(path / name, name if relative == "." else relative + "/" + name)
        elif stat.S_ISREG(mode):
            counts["regular_files"] += 1
        else:
            raise UnsafeSubmittedTree(f"Submitted special file is not allowed: {relative}")

    if not stat.S_ISDIR(root.lstat().st_mode) or root.is_symlink():
        raise UnsafeSubmittedTree("Submitted workspace must be an ordinary directory")
    visit(root, ".")
    return {"status": "pass", **counts}
