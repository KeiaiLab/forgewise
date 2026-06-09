# forgewise — multi-stage Docker 이미지
# 빌드: docker buildx build -t forgewise .
# 실행: docker run --rm forgewise --help
#
# §2 정책: 기본 빌더(default)만 사용. 멀티아키텍처 금지.
# --platform 생략 → 자동 linux/amd64.

# ── Stage 1: builder ──────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# 의존성 캐시 레이어: pyproject.toml + README (hatchling 메타데이터 필수)
COPY pyproject.toml README.md ./

# 소스 복사 (hatchling 빌드에 forgewise/ 필요)
COPY forgewise/ forgewise/

# wheel 빌드 + 설치 → 불필요 패키지 제거 (이미지 크기 최적화)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . \
    && pip uninstall -y pip setuptools wheel \
    && find /usr/local/lib/python3.11/site-packages -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true \
    && find /usr/local/lib/python3.11/site-packages -name '*.pyc' -delete 2>/dev/null; true \
    && rm -rf /usr/local/lib/python3.11/site-packages/pip* \
              /usr/local/lib/python3.11/site-packages/setuptools* \
              /usr/local/lib/python3.11/site-packages/wheel* \
              /usr/local/lib/python3.11/site-packages/_distutils_hack* \
              /usr/local/lib/python3.11/site-packages/distutils-precedence.pth

# ── Stage 2: runtime ──────────────────────────────────────────────
FROM python:3.11-slim

LABEL org.opencontainers.image.title="forgewise" \
      org.opencontainers.image.description="Open-source MCP-native developer intelligence for code forges" \
      org.opencontainers.image.source="https://github.com/keiailab/forgewise" \
      org.opencontainers.image.licenses="MIT"

# 런타임 사용자 (non-root) + 불필요 파일 제거 (이미지 크기 최적화)
RUN groupadd --gid 1000 forgewise \
    && useradd --uid 1000 --gid forgewise --create-home forgewise \
    && rm -rf /usr/local/lib/python3.11/ensurepip \
              /usr/local/lib/python3.11/idlelib \
              /usr/local/lib/python3.11/tkinter \
              /usr/local/lib/python3.11/turtle* \
              /usr/local/lib/python3.11/turtledemo \
              /usr/local/lib/python3.11/lib2to3 \
              /usr/local/lib/python3.11/distutils \
              /usr/local/lib/python3.11/pydoc_data \
              /usr/local/lib/python3.11/test \
              /usr/local/lib/python3.11/unittest \
              /usr/local/lib/python3.11/site-packages/pip* \
              /usr/local/lib/python3.11/site-packages/setuptools* \
              /usr/local/lib/python3.11/site-packages/wheel* \
              /usr/local/lib/python3.11/site-packages/_distutils_hack* \
              /usr/local/lib/python3.11/site-packages/distutils-precedence.pth \
    && find /usr/local -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true

# builder 에서 설치된 패키지 + entry point 스크립트 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/forgewise* /usr/local/bin/

WORKDIR /workspace

USER forgewise

# 기본 entry point: forgewise CLI
# 다른 entry point 사용 시: docker run --entrypoint forgewise-mcp forgewise
#                          docker run --entrypoint forgewise-http forgewise
ENTRYPOINT ["forgewise"]
