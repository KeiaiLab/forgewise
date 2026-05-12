from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from forgewise.features import ForgeWise, to_pretty_json


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    fw = ForgeWise(Path(args.repo))
    result = _dispatch(fw, args)
    print(to_pretty_json(result))
    if args.command == "check" and result["status"] == "fail":
        return 1
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forgewise")
    parser.add_argument("--repo", default=".", help="저장소 루트")
    sub = parser.add_subparsers(dest="command", required=True)

    explain = sub.add_parser("explain", help="코드 설명")
    explain.add_argument("path")
    explain.add_argument("--start", type=int)
    explain.add_argument("--end", type=int)

    for name in ("refactor", "fix", "test-generate", "vuln-explain", "vuln-resolve"):
        command = sub.add_parser(name)
        command.add_argument("path")

    chat = sub.add_parser("chat")
    chat.add_argument("question")

    root = sub.add_parser("root-cause")
    root.add_argument("log")

    mr = sub.add_parser("mr-summary")
    mr.add_argument("--base", default="HEAD~1")

    merge_commit = sub.add_parser("merge-commit-message")
    merge_commit.add_argument("--base", default="HEAD~1")

    issue = sub.add_parser("issue-description")
    issue.add_argument("prompt")

    discussion = sub.add_parser("discussion-summary")
    discussion.add_argument("text")

    sub.add_parser("suggestions")
    sub.add_parser("review")
    sub.add_parser("review-summary")
    sub.add_parser("check")
    sub.add_parser("trends")
    return parser


def _dispatch(fw: ForgeWise, args: argparse.Namespace) -> dict[str, object]:
    command = str(args.command)
    if command == "explain":
        return fw.code_explanation(str(args.path), args.start, args.end)
    if command == "refactor":
        return fw.refactor_code(str(args.path))
    if command == "fix":
        return fw.fix_code(str(args.path))
    if command == "test-generate":
        return fw.test_generation(str(args.path))
    if command == "vuln-explain":
        return fw.vulnerability_explanation(str(args.path))
    if command == "vuln-resolve":
        return fw.vulnerability_resolution(str(args.path))
    if command == "chat":
        return fw.duo_chat(str(args.question))
    if command == "suggestions":
        return fw.code_suggestions()
    if command in {"review", "check"}:
        return fw.code_review()
    if command == "root-cause":
        return fw.root_cause_analysis(str(args.log))
    if command == "mr-summary":
        return fw.merge_request_summary(str(args.base))
    if command == "merge-commit-message":
        return fw.merge_commit_message_generation(str(args.base))
    if command == "review-summary":
        return fw.code_review_summary()
    if command == "issue-description":
        return fw.issue_description_generation(str(args.prompt))
    if command == "discussion-summary":
        return fw.discussion_summary(str(args.text))
    if command == "trends":
        return fw.sdlc_trends()
    raise SystemExit(f"unknown command: {command}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
