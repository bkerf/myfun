#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_ROOT="$ROOT_DIR/.tmp/git-quick-push-test-$$"
REMOTE_DIR="$TEST_ROOT/remote.git"
WORK_DIR="$TEST_ROOT/work"
STUB_BIN="$TEST_ROOT/bin"
CODEX_LOG="$TEST_ROOT/codex.log"

export PATH="$ROOT_DIR:$STUB_BIN:$PATH"
export CODEX_QUICK_PUSH_TEST_LOG="$CODEX_LOG"

mkdir -p "$STUB_BIN"

cat > "$STUB_BIN/codex" <<'STUB'
#!/usr/bin/env bash
printf "%s\n" "$*" >> "$CODEX_QUICK_PUSH_TEST_LOG"
original_args="$*"

output_file=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    -o|--output-last-message)
      shift
      output_file="$1"
      ;;
  esac
  shift || true
done

case "$original_args" in
  *"gpt-5.3-codex-spark"*)
    if [ "${CODEX_QUICK_PUSH_TEST_FAIL:-0}" = "1" ]; then
      exit 42
    fi
    printf "codex progress noise\n"
    if [ -n "$output_file" ]; then
      printf "feat: add generated commit support\n\nExtra explanation that must be ignored.\n" > "$output_file"
    fi
    ;;
  *)
    exit 42
    ;;
esac
STUB
chmod +x "$STUB_BIN/codex"

git init --bare "$REMOTE_DIR" >/dev/null
git init -b main "$WORK_DIR" >/dev/null 2>&1 || {
  git init "$WORK_DIR" >/dev/null
  git -C "$WORK_DIR" checkout -b main >/dev/null
}
git -C "$WORK_DIR" config user.email "git-quick-push-test@example.com"
git -C "$WORK_DIR" config user.name "Git Quick Push Test"
git -C "$WORK_DIR" remote add origin "$REMOTE_DIR"

printf "hello\n" > "$WORK_DIR/README.md"
git -C "$WORK_DIR" quick-push

test "$(git -C "$WORK_DIR" rev-list --count HEAD)" = "1"
test -z "$(git -C "$WORK_DIR" status --porcelain)"
test "$(git -C "$WORK_DIR" rev-parse --abbrev-ref --symbolic-full-name '@{u}')" = "origin/main"
git -C "$REMOTE_DIR" rev-parse --verify refs/heads/main >/dev/null
test "$(git -C "$WORK_DIR" log -1 --pretty=%s)" = "docs: update docs"
test ! -s "$CODEX_LOG"

printf "more\n" >> "$WORK_DIR/README.md"
git -C "$WORK_DIR" quick-push "docs: custom message"

test "$(git -C "$WORK_DIR" rev-list --count HEAD)" = "2"
test -z "$(git -C "$WORK_DIR" status --porcelain)"
test "$(git -C "$WORK_DIR" log -1 --pretty=%s)" = "docs: custom message"
test ! -s "$CODEX_LOG"

printf "ai\n" > "$WORK_DIR/feature.txt"
git -C "$WORK_DIR" quick-push -a

test "$(git -C "$WORK_DIR" rev-list --count HEAD)" = "3"
test -z "$(git -C "$WORK_DIR" status --porcelain)"
test "$(git -C "$WORK_DIR" log -1 --pretty=%s)" = "feat: add generated commit support"
grep -q -- "-m gpt-5.3-codex-spark" "$CODEX_LOG"

printf "fallback\n" > "$WORK_DIR/fallback.txt"
CODEX_QUICK_PUSH_TEST_FAIL=1 git -C "$WORK_DIR" quick-push -a

test "$(git -C "$WORK_DIR" rev-list --count HEAD)" = "4"
test -z "$(git -C "$WORK_DIR" status --porcelain)"
test "$(git -C "$WORK_DIR" log -1 --pretty=%s)" = "chore: update workspace"
