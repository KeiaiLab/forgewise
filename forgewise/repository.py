"""파일 시스템 기반 저장소 추상화."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
}

TEXT_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".json",
    ".kt",
    ".md",
    ".py",
    ".rs",
    ".sh",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}


def line_slice(text: str, start: int | None = None, end: int | None = None) -> str:
    lines = text.splitlines()
    first = 1 if start is None else max(1, start)
    last = len(lines) if end is None else min(len(lines), end)
    if first > last:
        return ""
    return "\n".join(lines[first - 1 : last])


@dataclass(frozen=True)
class Repository:
    root: Path
    max_file_bytes: int = 512_000

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", self.root.resolve())

    def iter_files(self) -> list[Path]:
        files: list[Path] = []
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(self.root)
            if any(part in IGNORED_DIRS for part in rel.parts):
                continue
            if path.suffix not in TEXT_SUFFIXES:
                continue
            if path.stat().st_size > self.max_file_bytes:
                continue
            files.append(rel)
        return sorted(files, key=lambda item: item.as_posix())

    def resolve_relative(self, path: str | Path) -> Path:
        rel = Path(path)
        candidate = rel.resolve() if rel.is_absolute() else (self.root / rel).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise ValueError(f"path escapes repository root: {path}")
        return candidate

    def read_text(self, path: str | Path) -> str:
        candidate = self.resolve_relative(path)
        return candidate.read_text(encoding="utf-8", errors="replace")
