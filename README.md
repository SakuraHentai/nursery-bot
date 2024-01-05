# 开局托儿所 bot

### 准备

1. 安装 [Python3.8+](https://www.python.org/downloads/)
2. 安装 [Tesseract](https://github.com/tesseract-ocr/tesseract?tab=readme-ov-file#installing-tesseract) , 安装后需要手动设定 PATH , 前往控制面板 - 系统 - 高级系统设置 - 环境变量 - 新建并添加你的安装目录
3. 安装依赖 `pip install -r requirements.txt`

### 使用

PC 微信打开游戏到游戏界面后, 确保界面无遮挡后, 运行

```bash
python entry.py
```

### 关于配置

配置文件在 `nursery/modules/config.py` 中, 配置都为 `1920` 分辨率下的

```python
# 截图游戏界面的大小
ORIGIN_WIDTH = 441

# 截图游戏界面左边界到游戏区域偏移
OFFSET_X = 12
# 截图游戏界面上边界到游戏区域偏移
OFFSET_TOP = 126
# 截图游戏界面下边界到游戏区域偏移
OFFSET_BOTTOM = 33

# 游戏的数字格子大小
GRID_SIZE = 32
# 游戏的数字格子间距
GRID_GAP = 10

```

### 未完善

- [ ] 测试高分屏
