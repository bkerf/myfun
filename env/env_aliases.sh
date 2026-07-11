#!/bin/zsh

log "========== 开始定义别名 =========="

alias claudex="claude --dangerously-skip-permissions"

_codex_with_clash_verge_proxy() {
    local proxy_url="${CODEX_CLASH_PROXY_URL:-http://127.0.0.1:7897}"
    local no_proxy="${CODEX_NO_PROXY:-localhost,127.0.0.1,::1}"

    HTTP_PROXY="$proxy_url" \
    HTTPS_PROXY="$proxy_url" \
    ALL_PROXY="$proxy_url" \
    http_proxy="$proxy_url" \
    https_proxy="$proxy_url" \
    all_proxy="$proxy_url" \
    NO_PROXY="$no_proxy" \
    no_proxy="$no_proxy" \
    codex "$@"
}

unalias ch cx 2>/dev/null

ch() {
    _codex_with_clash_verge_proxy --yolo -c 'model_reasoning_effort="high"' "$@"
}

cx() {
    _codex_with_clash_verge_proxy --yolo -c 'model_reasoning_effort="xhigh"' "$@"
}

log "========== 别名定义完成 =========="
