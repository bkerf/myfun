#!/bin/zsh

# =====================================
# 定义日志函数，包含微秒级时间戳
# =====================================
log() {
#    local now="${EPOCHREALTIME}"
#    # 使用 Python 格式化时间戳，包含微秒
#    local datetime=$(python3 -c "import datetime; print(datetime.datetime.fromtimestamp(${now}).strftime('%Y-%m-%d %H:%M:%S.%f'))")
#    echo "[$datetime] $1"
}

log "========== 初始化 env_logging.sh 脚本开始 =========="
log "========== env_logging.sh 脚本初始化完成 =========="