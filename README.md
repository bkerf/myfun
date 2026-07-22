# myfun

Shell 环境配置和工具脚本集合。

## 📚 文档索引

| 文档 | 说明 |
|------|------|
| [CODE_CONVENTIONS.md](docs/CODE_CONVENTIONS.md) | 代码规范 |
| [BEST_PRACTICES.md](docs/BEST_PRACTICES.md) | 最佳实践 |

---

## 🚀 快速开始

在 `~/.zshrc` 中添加：

```bash
source /Users/ok/github/myfun/env/env.sh
```

---

## 📁 目录结构

```
myfun/
├── env/              # Shell 环境配置
│   ├── env.sh        # 主入口
│   ├── env_aliases.sh
│   ├── env_functions.sh
│   ├── env_path.sh
│   ├── env_variables.sh
│   └── ...
└── docs/             # 文档
```

---

## 常用工具

| 命令 | 说明 |
|------|------|
| `tms` | 打开 tmux session/window 选择器，支持方向键选择、Enter 直接进入 window、`n` 新建 session、`d`/`x` 关闭、`r` 刷新、`q` 退出 |
| `tms --list` | 非交互列出当前 tmux sessions 和 windows |
| `tmuxp reload [session...]` | 重载指定的 tmuxp session；不指定名称时关闭当前 server 的全部 session 并恢复其中的 tmuxp session |

`tmuxp reload` 默认展示关闭/重载计划并要求确认。常用选项：

- `tmuxp reload okpay`：只关闭并重新加载 `okpay`，保留其他 session。
- `tmuxp reload`：关闭当前 server 的全部 session，再恢复关闭前运行的 tmuxp session。
- `tmuxp reload --dry-run`：只检查当前 session 与 tmuxp 配置的映射。
- `tmuxp reload -y`：跳过确认，适合明确的非交互调用。
- `tmuxp reload --allow-unmanaged`：同时关闭没有 tmuxp 配置、因而无法恢复的 session。

若命令在目标 tmux server 内运行，会先启动脱离 tmux 的后台 worker，再关闭 server；默认日志位于
`~/.local/state/myfun/tmuxp-reload.log`。原生 `tmuxp` 的其他子命令保持不变。

---

##  环境配置说明

| 文件 | 说明 |
|------|------|
| `env.sh` | 主入口，加载其他配置 |
| `env_aliases.sh` | 命令别名 |
| `env_functions.sh` | 自定义函数 |
| `env_path.sh` | PATH 环境变量 |
| `env_variables.sh` | 其他环境变量 |
| `env_tools.sh` | 工具配置 |
| `env_other.sh` | 其他配置 |
| `env_logging.sh` | 日志配置 |

敏感环境变量保存在未跟踪的 `env/env_secrets.local.sh` 中；也可通过
`MYFUN_SECRETS_FILE` 指定其他本机配置文件。
