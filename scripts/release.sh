#!/usr/bin/env bash
#
# forgewise 수동 release 스크립트 (Python 패키지 + MCP server).
#
# 사용:
#   bash scripts/release.sh v0.1.0
#
# 동작:
#   1. tag 형식 검증 (vMAJOR.MINOR.PATCH).
#   2. working tree clean 검증.
#   3. branch=main 검증.
#   4. 로컬 게이트 — make check (ruff + mypy --strict + pytest).
#   5. version 정합 — pyproject.toml [project] version.
#   6. CHANGELOG.md 갱신 (사람 prompt).
#   7. python build — uv build → dist/.
#   8. tag + push origin.
#   9. gh release create — dist/ artifact 첨부.
#  10. (옵션) PyPI publish — twine upload (수동 결정).
#
# 사전조건:
#   - git remote 'origin' 설정 + main branch 권한.
#   - uv 설치 (https://docs.astral.sh/uv/).
#   - gh CLI 인증 (gh auth status).
#   - (선택) twine 설치 — PyPI publish (uv tool install twine).
#   - (선택) git-cliff — CHANGELOG/release body 자동 (brew install git-cliff).
#
# RFC-0002 정합: 본 스크립트는 *수동* 실행. GHA 미사용 (forgewise 는
# .github/workflows/ 부재 — Python 패키지 native CI/CD 부재 정책).

set -euo pipefail

usage() {
  echo "Usage: $0 <version>"
  echo "  version: vMAJOR.MINOR.PATCH (e.g. v0.1.0)"
  exit 1
}

VERSION="${1:-}"
[[ -z "$VERSION" ]] && usage

# 1. tag 형식
if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "❌ Invalid version: $VERSION (expected vMAJOR.MINOR.PATCH)" >&2
  exit 1
fi
VERSION_NUMERIC="${VERSION#v}"

# 2. working tree clean
if [[ -n "$(git status --porcelain)" ]]; then
  echo "❌ Working tree not clean. Stash or commit first." >&2
  git status --short >&2
  exit 1
fi

# 3. branch=main
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" != "main" ]]; then
  echo "❌ Not on main branch (current: $BRANCH)" >&2
  exit 1
fi

# 3.5. 동기화
git fetch origin main
if ! git merge-base --is-ancestor origin/main HEAD; then
  echo "❌ Local main is behind origin/main. Pull first." >&2
  exit 1
fi

# 4. 로컬 게이트
echo "🔍 Running make check (ruff + mypy strict + pytest)..."
if [[ -f Makefile ]] && grep -q "^check:" Makefile; then
  make check
else
  uv run ruff check forgewise tests
  uv run mypy --strict forgewise tests
  uv run pytest -q
fi

# 5. version 정합
PYPROJECT_VERSION=$(grep -E '^version\s*=' pyproject.toml | head -1 | sed -E 's/version\s*=\s*"([^"]+)"/\1/')
if [[ "$PYPROJECT_VERSION" != "$VERSION_NUMERIC" ]]; then
  echo "❌ Version mismatch: pyproject.toml=$PYPROJECT_VERSION vs requested=$VERSION_NUMERIC" >&2
  echo "   Update pyproject.toml [project] version first." >&2
  exit 1
fi

# 6. CHANGELOG
if [[ -f CHANGELOG.md ]]; then
  if command -v git-cliff >/dev/null; then
    git-cliff --tag "$VERSION" -o CHANGELOG.md
    git add CHANGELOG.md
    GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-$(git config user.name)}" \
    GIT_AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-$(git config user.email)}" \
    git commit -s -m "chore(release): CHANGELOG for $VERSION (git-cliff)"
    git push origin main
  else
    echo "⚠️  git-cliff 미설치. CHANGELOG.md 수동 갱신 + commit + push 필요."
    read -p "CHANGELOG.md 갱신 완료? (y/N) " ans
    [[ "$ans" != "y" ]] && exit 1
  fi
fi

# 7. python build
echo "📦 Building Python distribution..."
rm -rf dist/
uv build
DIST_FILES=$(ls dist/*.whl dist/*.tar.gz 2>/dev/null | tr '\n' ' ')
[[ -z "$DIST_FILES" ]] && { echo "❌ dist/ empty after uv build" >&2; exit 1; }
echo "   → $DIST_FILES"

# 8. tag + push
echo "🏷️  Creating tag $VERSION..."
git tag -a "$VERSION" -m "Release $VERSION

forgewise $VERSION

See CHANGELOG.md for details.
"
git push origin "$VERSION"

# 9. GitHub Release
RELEASE_BODY=""
if command -v git-cliff >/dev/null; then
  RELEASE_BODY=$(git-cliff --tag "$VERSION" --strip all)
elif [[ -f CHANGELOG.md ]]; then
  RELEASE_BODY=$(awk "/## \[$VERSION_NUMERIC\]/,/## \[/" CHANGELOG.md | head -n -1)
fi

echo "🚀 Creating GitHub release..."
if [[ -n "$RELEASE_BODY" ]]; then
  gh release create "$VERSION" $DIST_FILES --title "$VERSION" --notes "$RELEASE_BODY"
else
  gh release create "$VERSION" $DIST_FILES --title "$VERSION" --generate-notes
fi

# 10. (옵션) PyPI publish
if command -v twine >/dev/null 2>&1; then
  read -p "📤 PyPI publish (twine upload dist/*)? (y/N) " ans
  if [[ "$ans" == "y" ]]; then
    twine upload dist/*
  else
    echo "   skip (twine upload dist/* 수동 실행 가능)"
  fi
else
  echo "   twine 미설치 — PyPI publish skip (uv tool install twine 권장)"
fi

echo "✅ Release $VERSION complete."
echo ""
echo "다음 단계:"
echo "  1. CHANGELOG.md 의 [Unreleased] 섹션 정리"
echo "  2. ROADMAP.md 의 v$VERSION_NUMERIC 항목 ✅ 마킹"
echo "  3. (PyPI publish 안 한 경우) twine upload dist/* 수동 실행"
echo "  4. release announce (Slack / Twitter / community)"
