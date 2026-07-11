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
