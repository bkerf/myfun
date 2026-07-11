# 脚本最佳实践

## 1. 文件结构

### 标准模板

```python
#!/usr/bin/env python3
"""
脚本名称: xxx.py
功能描述: 一句话说明
用法: python xxx.py <参数>
依赖: PIL, requests
"""

import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: xxx.py <arg>")
        sys.exit(1)
    
    # 主逻辑
    pass

if __name__ == "__main__":
    main()
```

---

## 2. 错误处理

### ✅ 推荐
```python
try:
    with open(path) as f:
        data = f.read()
except FileNotFoundError:
    print(f"Error: {path} not found")
    sys.exit(1)
```

### ❌ 避免
```python
f = open(path)  # 不处理异常
data = f.read()
```

---

## 3. 参数处理

### 简单参数
```python
if len(sys.argv) != 2:
    print("Usage: script.py <folder>")
    sys.exit(1)
folder = sys.argv[1]
```

### 复杂参数（使用 argparse）
```python
import argparse
parser = argparse.ArgumentParser(description='处理图片')
parser.add_argument('input', help='输入文件夹')
parser.add_argument('-o', '--output', default='./out')
args = parser.parse_args()
```

---

## 4. 路径处理

```python
import os

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 拼接路径
output = os.path.join(folder, "output")

# 检查存在
if not os.path.exists(folder):
    print(f"Error: {folder} does not exist")
    sys.exit(1)
```

---

## 5. 日志输出

```python
# 简单场景
print(f"Processing: {filename}")
print(f"Done: {count} files processed")

# 复杂场景使用 logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Processing {filename}")
```

---

## 6. Shell 脚本

### 安全设置
```bash
#!/bin/bash
set -euo pipefail  # 遇错即停，未定义变量报错
```

### 参数检查
```bash
if [ $# -lt 1 ]; then
    echo "Usage: $0 <arg>"
    exit 1
fi
```

---

## 7. 代码示例参考

参考项目中的 [appleImage.py](../appleImage.py)：
- 清晰的函数划分
- 完整的参数检查
- 合理的目录创建逻辑
