"""Python 소스 정적 분석 — 심볼 추출, 리팩토링 제안, 테스트 스켈레톤 생성."""

from __future__ import annotations

import ast
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from forgewise.repository import Repository


@dataclass(frozen=True)
class Suggestion:
    rule_id: str
    path: str
    line: int
    severity: str
    message: str
    suggestion: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def python_symbols(text: str) -> dict[str, list[str]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {"classes": [], "functions": [], "imports": []}

    classes: list[str] = []
    functions: list[str] = []
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return {
        "classes": sorted(set(classes)),
        "functions": sorted(set(functions)),
        "imports": sorted(set(imports)),
    }


def refactor_suggestions(path: str, text: str) -> list[Suggestion]:
    suggestions: list[Suggestion] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if len(line) > 120:
            suggestions.append(
                Suggestion(
                    "long-line",
                    path,
                    lineno,
                    "info",
                    "120자를 넘는 줄입니다.",
                    "표현식을 나누거나 작은 helper로 추출하세요.",
                )
            )
        if stripped == "except:":
            suggestions.append(
                Suggestion(
                    "bare-except",
                    path,
                    lineno,
                    "warning",
                    "bare except는 시스템 종료와 취소 예외까지 삼킬 수 있습니다.",
                    "구체적인 예외 타입을 지정하고 에러 경로를 테스트하세요.",
                )
            )

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return suggestions

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            length = getattr(node, "end_lineno", node.lineno) - node.lineno + 1
            if length > 50:
                suggestions.append(
                    Suggestion(
                        "large-function",
                        path,
                        node.lineno,
                        "info",
                        f"{node.name} 함수가 {length}줄입니다.",
                        "입출력 경계가 분명한 단계별 함수로 분리하세요.",
                    )
                )
    return suggestions


def test_skeleton_for_python(path: str, text: str) -> tuple[str, str]:
    symbols = python_symbols(text)
    module_name = Path(path).stem
    lines = [
        "from __future__ import annotations",
        "",
        f"import {module_name}",
        "",
        "",
    ]
    for name in symbols["functions"]:
        if name.startswith("_"):
            continue
        lines.extend(
            [
                f"def test_{name}() -> None:",
                f"    # TODO: arrange inputs for {module_name}.{name}",
                f"    assert callable({module_name}.{name})",
                "",
                "",
            ]
        )
    if len(lines) == 5:
        lines.extend(
            [
                "def test_module_imports() -> None:",
                f"    assert {module_name} is not None",
                "",
            ]
        )
    return f"tests/test_{module_name}.py", "\n".join(lines).rstrip() + "\n"


def retrieve_context(repo: Repository, question: str, limit: int = 5) -> list[dict[str, Any]]:
    terms = {term.lower() for term in re.findall(r"[A-Za-z_][A-Za-z0-9_가-힣-]*", question)}
    scored: list[tuple[int, Path, str]] = []
    for rel in repo.iter_files():
        text = repo.read_text(rel)
        lowered = text.lower()
        score = sum(lowered.count(term) for term in terms)
        if score:
            scored.append((score, rel, text))
    scored.sort(key=lambda item: (-item[0], item[1].as_posix()))
    matches: list[dict[str, Any]] = []
    for score, rel, text in scored[:limit]:
        excerpt = "\n".join(text.splitlines()[:20])
        matches.append({"path": rel.as_posix(), "score": score, "excerpt": excerpt})
    return matches


def language_trends(repo: Repository) -> dict[str, Any]:
    counter: Counter[str] = Counter(path.suffix.lstrip(".") or "text" for path in repo.iter_files())
    return {"files": sum(counter.values()), "languages": dict(sorted(counter.items()))}
