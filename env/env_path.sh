#!/bin/zsh

log "========== 开始更新 PATH =========="

# 定义一个函数用于安全地添加 PATH，避免重复
add_to_path() {
    case ":$PATH:" in
        *":$1:"*) ;;
        *) export PATH="$1:$PATH" && log "更新 PATH 添加 $1" ;;
    esac
}

# 添加各个路径，避免重复添加
add_to_path "/opt/homebrew/bin"
add_to_path "/usr/local/bin"
add_to_path "/usr/bin"
add_to_path "/bin"
add_to_path "/usr/sbin"
add_to_path "/sbin"
add_to_path "/Applications/Visual Studio Code.app/Contents/Resources/app/bin"
add_to_path "/opt/homebrew/opt/sqlite/bin"
add_to_path "/Users/ok/github/myfun"

if command -v pyenv >/dev/null 2>&1; then
    add_to_path "$(pyenv root)/shims"
fi

log "========== PATH 更新完成 =========="
