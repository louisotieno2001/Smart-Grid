# Author: Jerry Onyango
# Contribution: Validates that Python source files include standardized author/contribution headers for governance consistency.

from __future__ import annotations

import argparse
from pathlib import Path

AUTHOR_LINE = "# Author: Jerry Onyango"
CONTRIB_PREFIX = "# Contribution: "


def _should_check(path: Path) -> bool:
    if path.suffix != ".py":
        return False
    parts = set(path.parts)
    if ".venv" in parts:
        return False
    return True


def _validate_file(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return f"{path}: not UTF-8"

    if len(lines) < 2:
        return f"{path}: file must have at least 2 lines for header"

    if lines[0].strip() != AUTHOR_LINE:
        return f"{path}: first line must be '{AUTHOR_LINE}'"

    if not lines[1].startswith(CONTRIB_PREFIX) or len(lines[1].strip()) <= len(CONTRIB_PREFIX):
        return f"{path}: second line must start with '{CONTRIB_PREFIX}' and include text"

    return None


def _collect_paths(args: list[str]) -> list[Path]:
    if args:
        return [Path(item) for item in args]

    repo_root = Path(__file__).resolve().parents[1]
    return sorted(
        [
            path
            for base in [repo_root / "src", repo_root / "scripts"]
            for path in base.rglob("*.py")
            if path.is_file()
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Python file headers")
    parser.add_argument("files", nargs="*", help="Optional explicit list of files")
    parsed = parser.parse_args()

    failures: list[str] = []
    for path in _collect_paths(parsed.files):
        if not path.exists() or not _should_check(path):
            continue
        failure = _validate_file(path)
        if failure:
            failures.append(failure)

    if failures:
        print("Header check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Header check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
