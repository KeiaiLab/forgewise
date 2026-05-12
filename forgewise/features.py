from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from forgewise.analysis import (
    language_trends,
    python_symbols,
    refactor_suggestions,
    retrieve_context,
    test_skeleton_for_python,
)
from forgewise.repository import Repository, line_slice
from forgewise.security import security_findings, security_fixes


class ForgeWise:
    def __init__(self, root: str | Path) -> None:
        self.repo = Repository(Path(root))

    def code_explanation(
        self, path: str, start: int | None = None, end: int | None = None
    ) -> dict[str, Any]:
        text = self.repo.read_text(path)
        selected = line_slice(text, start, end)
        return {
            "feature": "code_explanation",
            "path": path,
            "slice": {
                "start": 1 if start is None else start,
                "end": len(text.splitlines()) if end is None else end,
                "content": selected,
            },
            "symbols": python_symbols(text),
            "summary": _summarize_code(path, text),
        }

    def refactor_code(self, path: str) -> dict[str, Any]:
        text = self.repo.read_text(path)
        suggestions = [item.to_dict() for item in refactor_suggestions(path, text)]
        return {"feature": "refactor_code", "path": path, "suggestions": suggestions}

    def fix_code(self, path: str) -> dict[str, Any]:
        text = self.repo.read_text(path)
        findings = security_findings(path, text)
        fixes = security_fixes(findings)
        return {
            "feature": "fix_code",
            "path": path,
            "fixes": [item.to_dict() for item in fixes],
        }

    def test_generation(self, path: str) -> dict[str, Any]:
        text = self.repo.read_text(path)
        target, content = test_skeleton_for_python(path, text)
        return {"feature": "test_generation", "source": path, "path": target, "content": content}

    def vulnerability_explanation(self, path: str) -> dict[str, Any]:
        text = self.repo.read_text(path)
        findings = [item.to_dict() for item in security_findings(path, text)]
        return {"feature": "vulnerability_explanation", "path": path, "findings": findings}

    def vulnerability_resolution(self, path: str) -> dict[str, Any]:
        text = self.repo.read_text(path)
        findings = security_findings(path, text)
        fixes = [item.to_dict() for item in security_fixes(findings)]
        return {"feature": "vulnerability_resolution", "path": path, "fixes": fixes}

    def duo_chat(self, question: str) -> dict[str, Any]:
        matches = retrieve_context(self.repo, question)
        answer = (
            "관련 코드 조각을 찾았습니다. 외부 LLM 없이 로컬 검색 결과만 반환합니다."
            if matches
            else "관련 코드 조각을 찾지 못했습니다."
        )
        return {"feature": "duo_chat", "question": question, "answer": answer, "matches": matches}

    def code_suggestions(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        for rel in self.repo.iter_files():
            path = rel.as_posix()
            text = self.repo.read_text(rel)
            findings.extend(item.to_dict() for item in refactor_suggestions(path, text))
            findings.extend(item.to_dict() for item in security_findings(path, text))
        return {"feature": "code_suggestions", "suggestions": findings}

    def code_review(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        for rel in self.repo.iter_files():
            path = rel.as_posix()
            text = self.repo.read_text(rel)
            findings.extend(item.to_dict() for item in security_findings(path, text))
            findings.extend(item.to_dict() for item in refactor_suggestions(path, text))
        return {
            "feature": "code_review",
            "findings": findings,
            "status": "fail" if findings else "pass",
        }

    def root_cause_analysis(self, log: str) -> dict[str, Any]:
        text = self._read_log_input(log)
        frames = []
        for match in re.finditer(r'File "([^"]+)", line (\d+)', text):
            frames.append({"path": match.group(1), "line": int(match.group(2))})
        error_line = next((line for line in reversed(text.splitlines()) if line.strip()), "")
        return {"feature": "root_cause_analysis", "error": error_line, "frames": frames}

    def merge_request_summary(self, base: str = "HEAD~1") -> dict[str, Any]:
        diff = _git_diff(self.repo.root, base)
        return {"feature": "merge_request_summary", "base": base, "summary": _summarize_diff(diff)}

    def merge_commit_message_generation(self, base: str = "HEAD~1") -> dict[str, Any]:
        diff = _git_diff(self.repo.root, base)
        summary = _summarize_diff(diff)
        files = summary["files"]
        noun = f"{len(files)} files" if files else "repository metadata"
        message = f"chore: update {noun}"
        return {
            "feature": "merge_commit_message_generation",
            "base": base,
            "message": message,
            "summary": summary,
        }

    def code_review_summary(self) -> dict[str, Any]:
        review = self.code_review()
        counts: dict[str, int] = {}
        for finding in review["findings"]:
            severity = str(finding.get("severity", "info"))
            counts[severity] = counts.get(severity, 0) + 1
        total = len(review["findings"])
        return {
            "feature": "code_review_summary",
            "status": review["status"],
            "total_findings": total,
            "by_severity": dict(sorted(counts.items())),
            "headline": "No review findings" if total == 0 else f"{total} review findings",
        }

    def issue_description_generation(self, prompt: str) -> dict[str, Any]:
        title = prompt.strip().rstrip(".") or "untitled issue"
        body = "\n".join(
            [
                f"## Summary\n{title}",
                "",
                "## Context\nGenerated locally by ForgeWise from the supplied issue prompt.",
                "",
                "## Acceptance Criteria",
                "- Reproduce or confirm the reported behavior.",
                "- Add or update tests that cover the fix.",
                "- Run the local project gate before merge.",
            ]
        )
        return {"feature": "issue_description_generation", "title": title, "body": body}

    def discussion_summary(self, text: str) -> dict[str, Any]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return {
            "feature": "discussion_summary",
            "messages": len(lines),
            "summary": lines[:3],
            "open_questions": [line for line in lines if "?" in line],
        }

    def sdlc_trends(self) -> dict[str, Any]:
        review = self.code_review()
        trends = language_trends(self.repo)
        trends["finding_count"] = len(review["findings"])
        return {"feature": "sdlc_trends", "trends": trends}

    def _read_log_input(self, log: str) -> str:
        candidate = self.repo.resolve_relative(log)
        if candidate.exists():
            return candidate.read_text(encoding="utf-8", errors="replace")
        return log


def _summarize_code(path: str, text: str) -> str:
    symbols = python_symbols(text) if path.endswith(".py") else {"classes": [], "functions": []}
    parts = []
    if symbols["classes"]:
        parts.append("classes=" + ", ".join(symbols["classes"]))
    if symbols["functions"]:
        parts.append("functions=" + ", ".join(symbols["functions"]))
    return "; ".join(parts) if parts else f"{len(text.splitlines())} lines"


def _git_diff(root: Path, base: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "diff", "--stat", "--find-renames", base],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return "git not available"
    if proc.returncode != 0:
        return proc.stderr.strip() or "no git diff available"
    return proc.stdout.strip() or "no changes"


def _summarize_diff(diff: str) -> dict[str, Any]:
    files: list[str] = []
    for line in diff.splitlines():
        if "|" in line:
            files.append(line.split("|", 1)[0].strip())
    return {"files": files, "raw": diff}


def to_pretty_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
