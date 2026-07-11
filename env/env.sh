#!/bin/zsh

# 引入日志函数
source "$(dirname "$0")/env_logging.sh"

log "========== 初始化 env.sh 主脚本开始 =========="

# 加载仅保存在本机的敏感环境变量
_myfun_secrets_file="${MYFUN_SECRETS_FILE:-$(dirname "$0")/env_secrets.local.sh}"
if [ -r "$_myfun_secrets_file" ]; then
  source "$_myfun_secrets_file"
fi
unset _myfun_secrets_file

# 引入环境变量设置
source "$(dirname "$0")/env_variables.sh"

# 引入 PATH 设置
source "$(dirname "$0")/env_path.sh"

# 引入工具初始化
source "$(dirname "$0")/env_tools.sh"

# 引入函数定义
source "$(dirname "$0")/env_functions.sh"

# 引入别名定义
source "$(dirname "$0")/env_aliases.sh"

# 引入其他设置
source "$(dirname "$0")/env_other.sh"

log "========== env.sh 主脚本初始化完成 =========="
