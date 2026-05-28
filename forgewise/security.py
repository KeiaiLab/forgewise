"""보안 취약점 정적 탐지 — hardcoded-secret, eval, shell=True."""

from __future__ import annotations

import ast
import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SecurityFinding:
    rule_id: str
    path: str
    line: int
    severity: str
    message: str
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SecurityFix:
    rule_id: str
    path: str
    line: int
    before: str
    suggestion: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


SECRET_RE = re.compile(
    r"(?i)\b[a-z0-9_-]*(api[_-]?key|token|secret|password)[a-z0-9_-]*\b\s*=\s*['\"][^'\"]{6,}['\"]"
)


def security_findings(path: str, text: str) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    lines = text.splitlines()
    for lineno, line in enumerate(lines, start=1):
        if SECRET_RE.search(line):
            findings.append(
                SecurityFinding(
                    "hardcoded-secret",
                    path,
                    lineno,
                    "high",
                    "하드코딩된 비밀값으로 보이는 문자열입니다.",
                    line.strip(),
                )
            )

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "eval":
                findings.append(
                    SecurityFinding(
                        "python-eval",
                        path,
                        node.lineno,
                        "critical",
                        "eval 호출은 임의 코드 실행으로 이어질 수 있습니다.",
                        lines[node.lineno - 1].strip(),
                    )
                )
            for keyword in node.keywords:
                if (
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                ):
                    findings.append(
                        SecurityFinding(
                            "shell-true",
                            path,
                            node.lineno,
                            "high",
                            "subprocess shell=True는 명령 주입 위험이 있습니다.",
                            lines[node.lineno - 1].strip(),
                        )
                    )
    return findings


def security_fixes(findings: list[SecurityFinding]) -> list[SecurityFix]:
    fixes: list[SecurityFix] = []
    for finding in findings:
        if finding.rule_id == "python-eval":
            suggestion = "가능하면 ast.literal_eval 또는 명시적 파서를 사용하세요."
        elif finding.rule_id == "shell-true":
            suggestion = "shell=True를 제거하고 인자를 list[str]로 전달하세요."
        elif finding.rule_id == "hardcoded-secret":
            suggestion = "환경변수나 비밀 관리자로 옮기고 테스트에는 stub 값을 주입하세요."
        else:
            suggestion = "위험한 입력 경계를 좁히고 회귀 테스트를 추가하세요."
        fixes.append(
            SecurityFix(
                finding.rule_id,
                finding.path,
                finding.line,
                finding.evidence,
                suggestion,
            )
        )
    return fixes
