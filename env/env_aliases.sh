#!/bin/zsh

log "========== 开始定义别名 =========="

alias claudex="claude --dangerously-skip-permissions"

_codex_with_clash_verge_proxy() {
    local preferred_codex="${MYFUN_CODEX_BIN:-}"
    local proxy_url="${CODEX_CLASH_PROXY_URL:-http://127.0.0.1:7897}"
    local no_proxy="${CODEX_NO_PROXY:-localhost,127.0.0.1,::1}"
    local codex_bin

    if [ -n "$preferred_codex" ]; then
        codex_bin="$preferred_codex"
    elif [ -n "${NVM_BIN:-}" ] && [ -x "$NVM_BIN/codex" ]; then
        codex_bin="$NVM_BIN/codex"
    else
        codex_bin="$(whence -p codex 2>/dev/null)"
    fi

    if [ -z "$codex_bin" ] || [ ! -x "$codex_bin" ]; then
        printf '%s\n' "Codex CLI is unavailable. Set MYFUN_CODEX_BIN or install codex." >&2
        return 127
    fi

    HTTP_PROXY="$proxy_url" \
    HTTPS_PROXY="$proxy_url" \
    ALL_PROXY="$proxy_url" \
    http_proxy="$proxy_url" \
    https_proxy="$proxy_url" \
    all_proxy="$proxy_url" \
    NO_PROXY="$no_proxy" \
    no_proxy="$no_proxy" \
    "$codex_bin" "$@"
}

unalias ch cx cm cu 2>/dev/null

ch() {
    _codex_with_clash_verge_proxy --yolo -c 'model_reasoning_effort="high"' "$@"
}

cx() {
    _codex_with_clash_verge_proxy --yolo -c 'model_reasoning_effort="xhigh"' "$@"
}

cm() {
    _codex_with_clash_verge_proxy --yolo -c 'model_reasoning_effort="max"' "$@"
}

cu() {
    _codex_with_clash_verge_proxy --yolo -c 'model_reasoning_effort="ultra"' "$@"
}

log "========== 别名定义完成 =========="
