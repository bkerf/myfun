#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_ROOT="$ROOT_DIR/.tmp/git-create-branch-test-$$"
REMOTE_DIR="$TEST_ROOT/remote.git"
WORK_DIR="$TEST_ROOT/work"
STUB_BIN="$TEST_ROOT/bin"
REAL_GIT="$(command -v git)"

export PATH="$ROOT_DIR:$PATH"

mkdir -p "$STUB_BIN"

cat > "$STUB_BIN/git" <<'STUB'
#!/usr/bin/env bash
if [ "$1" = "ls-remote" ]; then
  printf "test git wrapper: git ls-remote is forbidden here\n" >&2
  exit 99
fi

exec "$GIT_CREATE_BRANCH_TEST_REAL_GIT" "$@"
STUB
chmod +x "$STUB_BIN/git"

run_create_branch() {
  local branch_input="$1"
  shift

  (
    cd "$WORK_DIR"
    export PATH="$STUB_BIN:$PATH"
    export GIT_CREATE_BRANCH_TEST_REAL_GIT="$REAL_GIT"
    printf "%s\n" "$branch_input" | git-create-branch "$@"
  )
}

git init --bare "$REMOTE_DIR" >/dev/null
git init -b main "$WORK_DIR" >/dev/null 2>&1 || {
  git init "$WORK_DIR" >/dev/null
  git -C "$WORK_DIR" checkout -b main >/dev/null
}
git -C "$WORK_DIR" config user.email "git-create-branch-test@example.com"
git -C "$WORK_DIR" config user.name "Git Create Branch Test"
git -C "$WORK_DIR" remote add origin "$REMOTE_DIR"

printf "base\n" > "$WORK_DIR/README.md"
git -C "$WORK_DIR" add README.md
git -C "$WORK_DIR" commit -m "chore: initial commit" >/dev/null
git -C "$WORK_DIR" push -u origin main >/dev/null

printf "base\nfeature\n" > "$WORK_DIR/README.md"
printf "notes\n" > "$WORK_DIR/notes.txt"

create_output="$(run_create_branch "Feature Launch" 2>&1)"
printf "%s\n" "$create_output" | grep -F "当前远程分支:"
printf "%s\n" "$create_output" | grep -F "  origin/main"

test "$(git -C "$WORK_DIR" branch --show-current)" = "feature-launch"
test "$(git -C "$WORK_DIR" rev-list --count HEAD)" = "2"
test -z "$(git -C "$WORK_DIR" status --porcelain)"
test "$(git -C "$WORK_DIR" rev-parse --abbrev-ref --symbolic-full-name '@{u}')" = "origin/feature-launch"
git -C "$REMOTE_DIR" rev-parse --verify refs/heads/feature-launch >/dev/null
test "$(git -C "$WORK_DIR" log -1 --pretty=%s)" = "chore: update workspace"
test "$(git -C "$WORK_DIR" show HEAD:README.md)" = "$(printf "base\nfeature")"
test "$(git -C "$WORK_DIR" show HEAD:notes.txt)" = "notes"

git -C "$WORK_DIR" checkout main >/dev/null
printf "custom\n" > "$WORK_DIR/custom.txt"

run_create_branch "Custom Message" -m "fix: custom branch commit"

test "$(git -C "$WORK_DIR" branch --show-current)" = "custom-message"
test "$(git -C "$WORK_DIR" rev-list --count HEAD)" = "2"
test -z "$(git -C "$WORK_DIR" status --porcelain)"
test "$(git -C "$WORK_DIR" rev-parse --abbrev-ref --symbolic-full-name '@{u}')" = "origin/custom-message"
git -C "$REMOTE_DIR" rev-parse --verify refs/heads/custom-message >/dev/null
test "$(git -C "$WORK_DIR" log -1 --pretty=%s)" = "fix: custom branch commit"
test "$(git -C "$WORK_DIR" show HEAD:custom.txt)" = "custom"

git -C "$WORK_DIR" checkout main >/dev/null

run_create_branch "Empty Branch"

test "$(git -C "$WORK_DIR" branch --show-current)" = "empty-branch"
test "$(git -C "$WORK_DIR" rev-list --count HEAD)" = "1"
test -z "$(git -C "$WORK_DIR" status --porcelain)"
test "$(git -C "$WORK_DIR" rev-parse --abbrev-ref --symbolic-full-name '@{u}')" = "origin/empty-branch"
git -C "$REMOTE_DIR" rev-parse --verify refs/heads/empty-branch >/dev/null
