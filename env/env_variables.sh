#!/bin/zsh

log "========== 开始设置环境变量 =========="

export HOMEBREW_NO_AUTO_UPDATE=1
log "设置 HOMEBREW_NO_AUTO_UPDATE"

export DISABLE_AUTO_UPDATE="true"
export DISABLE_UPDATE_PROMPT="true"
export UPDATE_ZSH_DAYS=999999
zstyle ':omz:update' mode disabled
log "禁用 oh-my-zsh 自动更新提示"

export JAVA_HOME=""
export CLASSPATH=""



export EDITOR=vim
log "设置 EDITOR"


export USER_NAME="ok"
log "设置 USER_NAME"

export DJANGO_TESTING_MODE=True
log "设置 DJANGO_TESTING_MODE"

export LOCAL_SQL=True
log "设置 LOCAL_SQL"

export DEBUG=True
log "设置 DEBUG"

export IS_DEBUG=True
log "设置 IS_DEBUG"

export IMAGEIO_FFMPEG_EXE="/opt/homebrew/bin/ffmpeg"
log "设置 IMAGEIO_FFMPEG_EXE"
export PUB_HOSTED_URL="https://pub.flutter-io.cn"
export FLUTTER_STORAGE_BASE_URL="https://storage.flutter-io.cn"

export ALTERNATE_EDITOR=""
log "设置 ALTERNATE_EDITOR"


export OLLAMA_API_BASE_URL="http://localhost:11434"

log "========== 环境变量设置完成 =========="
