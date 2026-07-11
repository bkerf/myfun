# myfun 代码规范

## Shell 脚本 (.sh)

### 文件头
```bash
#!/bin/bash
# 脚本描述
# 用法: script.sh <参数>
```

### 命名
- 文件名：小写 + 下划线，如 `env_aliases.sh`
- 变量名：大写 + 下划线，如 `MY_PATH`
- 函数名：小写 + 下划线，如 `my_function()`

### 格式
- 缩进：2 空格
- 字符串：优先双引号 `"$var"`
- 命令替换：`$(command)` 而非反引号

---

## Python 脚本 (.py)

### 文件头
```python
#!/usr/bin/env python3
"""
脚本描述
用法: python script.py <参数>
"""
```

### 命名
- 文件名：小写 + 下划线，如 `apple_image.py`
- 函数/变量：小写 + 下划线，如 `resize_image`
- 类名：大驼峰，如 `ImageProcessor`
- 常量：大写 + 下划线，如 `MAX_SIZE`

### 格式
- 遵循 PEP 8
- 缩进：4 空格
- 行宽：≤ 120 字符

---

## 通用规则

1. **注释**：关键逻辑必须注释
2. **错误处理**：脚本需处理参数缺失/文件不存在等情况
3. **依赖**：在文件头或 README 中说明依赖
