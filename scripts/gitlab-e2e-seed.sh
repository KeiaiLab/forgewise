#!/usr/bin/env bash
# gitlab-e2e-seed.sh — GitLab CE E2E 테스트 초기 데이터 생성
#
# GitLab CE 컨테이너 내부에서 실행:
#   docker compose -f docker-compose.e2e.yml exec gitlab bash /opt/gitlab-e2e-seed.sh
#
# 생성 항목:
#   1. Personal Access Token (root 사용자, 값: e2e-test-token)
#   2. 테스트 프로젝트 (forgewise-e2e-test)
#   3. 테스트 이슈 1건
#
# 주의: GitLab CE health check 통과 후 실행해야 합니다.

set -euo pipefail

TOKEN_VALUE="${GITLAB_SEED_E2E_TOKEN:-e2e-test-token}"
PROJECT_NAME="forgewise-e2e-test"

echo "=== ForgeWise E2E seed 시작 ==="

gitlab-rails runner - <<RUBY
user = User.find_by(username: 'root')
unless PersonalAccessToken.find_by(name: 'e2e-test-token')
  token = PersonalAccessToken.new(
    user: user,
    name: 'e2e-test-token',
    token_digest: Gitlab::CryptoHelper.sha256('${TOKEN_VALUE}'),
    scopes: [:api, :read_api, :read_user, :read_repository, :write_repository],
    expires_at: 1.year.from_now
  )
  token.set_token('${TOKEN_VALUE}')
  token.save!
  puts "PAT 생성 완료: e2e-test-token"
else
  puts "PAT 이미 존재: e2e-test-token"
end

unless Project.find_by_full_path("root/${PROJECT_NAME}")
  project = Projects::CreateService.new(
    user,
    name: '${PROJECT_NAME}',
    path: '${PROJECT_NAME}',
    visibility_level: Gitlab::VisibilityLevel::PRIVATE,
    initialize_with_readme: true
  ).execute[:project]
  puts "프로젝트 생성 완료: #{project.full_path}"

  issue = Issues::CreateService.new(
    container: project,
    current_user: user,
    params: {
      title: 'E2E 테스트 이슈',
      description: 'ForgeWise E2E 테스트용 이슈입니다.'
    }
  ).execute[:issue]
  puts "이슈 생성 완료: ##{issue.iid}"

  project.repository.create_file(
    user,
    'src/hello.py',
    "def hello():\\n    return 'ForgeWise E2E'\\n",
    message: 'E2E seed: hello.py 추가',
    branch_name: project.default_branch
  )
  puts "파일 생성 완료: src/hello.py"
else
  puts "프로젝트 이미 존재: root/${PROJECT_NAME}"
end

puts "=== ForgeWise E2E seed 완료 ==="
RUBY
