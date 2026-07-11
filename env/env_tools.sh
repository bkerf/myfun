#!/bin/zsh

log "========== 开始初始化工具 =========="

## 初始化 jenv
#log "初始化 jenv"
#if command -v jenv >/dev/null 2>&1; then
#    eval "$(jenv init -)"
#    log "完成初始化 jenv"
#else
#    log "jenv 未安装，跳过初始化"
#fi
#
## 初始化 tomo
#log "初始化 tomo"
#if command -v tomo >/dev/null 2>&1; then
#    eval "$(tomo completion-script)"
#    log "完成初始化 tomo"
#else
#    log "tomo 未安装，跳过初始化"
#fi
#
## 初始化 rbenv
#log "初始化 rbenv"
#if command -v rbenv >/dev/null 2>&1; then
#    eval "$(rbenv init -)"
#    log "完成初始化 rbenv"
#else
#    log "rbenv 未安装，跳过初始化"
#fi

# 初始化 pyenv（延迟加载以加速启动）
log "初始化 pyenv"
if command -v pyenv >/dev/null 2>&1; then
    # 必须首先设置 PYENV_ROOT，否则 pyenv 无法正常工作
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
    
    # 延迟加载 pyenv 的完整初始化
    pyenv() {
        unset -f pyenv python pip python3
        export PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
        eval "$(command pyenv init --path 2>/dev/null || true)"
        eval "$(command pyenv init - 2>/dev/null || true)"
        command pyenv "$@"
    }
    
    # 同时也延迟加载常用 python 命令
    python() {
        unset -f pyenv python pip python3
        export PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
        eval "$(command pyenv init --path 2>/dev/null || true)"
        command python "$@"
    }
    python3() {
        unset -f pyenv python pip python3
        export PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
        eval "$(command pyenv init --path 2>/dev/null || true)"
        command python3 "$@"
    }
    pip() {
        unset -f pyenv python pip python3
        export PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
        eval "$(command pyenv init --path 2>/dev/null || true)"
        command pip "$@"
    }
    
    log "完成初始化 pyenv（延迟加载模式）"
else
    log "pyenv 未安装，跳过初始化"
fi

# 懒加载 nvm (大幅提升启动速度)
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    # 读取 NVM default 别名指定的版本（而不是最新版本）
    if [ -f "$NVM_DIR/alias/default" ]; then
        DEFAULT_NODE_VERSION=$(cat "$NVM_DIR/alias/default")
    fi
    
    # 如果没有 default 别名，fallback 到最新版本
    if [ -z "$DEFAULT_NODE_VERSION" ] && [ -d "$NVM_DIR/versions/node" ]; then
        DEFAULT_NODE_VERSION=$(ls "$NVM_DIR/versions/node" 2>/dev/null | sort -V | tail -1)
    fi
    
    # 添加默认 node 到 PATH
    if [ -n "$DEFAULT_NODE_VERSION" ] && [ -d "$NVM_DIR/versions/node/v$DEFAULT_NODE_VERSION/bin" ]; then
        export PATH="$NVM_DIR/versions/node/v$DEFAULT_NODE_VERSION/bin:$PATH"
        log "已添加 node v$DEFAULT_NODE_VERSION 到 PATH"
    elif [ -n "$DEFAULT_NODE_VERSION" ] && [ -d "$NVM_DIR/versions/node/$DEFAULT_NODE_VERSION/bin" ]; then
        # 兼容没有 v 前缀的情况
        export PATH="$NVM_DIR/versions/node/$DEFAULT_NODE_VERSION/bin:$PATH"
        log "已添加 node $DEFAULT_NODE_VERSION 到 PATH"
    fi
    
    # 定义懒加载函数（包括 claude）
    nvm() {
        unset -f nvm node npm npx pnpm claude
        . "$NVM_DIR/nvm.sh"
        nvm "$@"
    }
    node() {
        unset -f nvm node npm npx pnpm claude
        . "$NVM_DIR/nvm.sh"
        node "$@"
    }
    npm() {
        unset -f nvm node npm npx pnpm claude
        . "$NVM_DIR/nvm.sh"
        npm "$@"
    }
    npx() {
        unset -f nvm node npm npx pnpm claude
        . "$NVM_DIR/nvm.sh"
        npx "$@"
    }
    pnpm() {
        unset -f nvm node npm npx pnpm claude
        . "$NVM_DIR/nvm.sh"
        pnpm "$@"
    }
    claude() {
        unset -f nvm node npm npx pnpm claude
        . "$NVM_DIR/nvm.sh"
        command claude "$@"
    }
    log "nvm 懒加载已配置"
else
    log "nvm.sh 不存在，跳过加载"
fi

log "工具初始化完成"