#!/bin/zsh

log "========== 开始其他设置 =========="

# 初始化 pyenv 只在 env_tools.sh 中完成，这里不再重复初始化
if command -v pyenv >/dev/null 2>&1; then
    log "pyenv 已在 env_tools.sh 中初始化，跳过重复初始化"
else
    log "pyenv 未安装，跳过初始化"
fi

# 以下 PATH 设置已移至 env_path.sh，避免重复添加
# node@16, qt@5, pyqt@5, e2fsprogs 等

# 不再重新初始化 pyenv
# export PATH="$(pyenv root)/shims:$PATH"
# log "更新 PATH 添加 pyenv shims"

# [[ -d "$PYENV_ROOT/bin" ]] && export PATH="$PYENV_ROOT/bin:$PATH"
# log "更新 PATH 添加 pyenv bin"

# 不再重新初始化 pyenv
# if command -v pyenv >/dev/null 2>&1; then
#     eval "$(pyenv init -)"
#     log "重新初始化 pyenv"
# else
#     log "pyenv 未安装，跳过重新初始化"
# fi

# 加载 JetBrains VM options 脚本
if [ -f "${HOME}/.jetbrains.vmoptions.sh" ]; then
    . "${HOME}/.jetbrains.vmoptions.sh"
    log "加载 JetBrains VM options 脚本"
else
    log "JetBrains VM options 脚本不存在，跳过加载"
fi

# 加载 acme.sh 环境变量
if [ -f "/Users/ok/.acme.sh/acme.sh.env" ]; then
    . "/Users/ok/.acme.sh/acme.sh.env"
    log "加载 acme.sh 环境变量"
else
    log "acme.sh 环境变量文件不存在，跳过加载"
fi

log "========== 其他设置完成 =========="
