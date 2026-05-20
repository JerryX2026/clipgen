# clipgen — 短视频自动生成器

> AI 配音 + 字幕 + 画面，一键生成短视频。一行命令，从文案到成品。

```bash
pip install clipgen
clipgen build my_video.yaml
```

---

## 它能做什么

**写一个 YAML 配置文件，描述你的视频脚本和画面，clipgen 自动完成一切：**

1. **生成画面** — 内置多套 Douyin 风格模板（对比 / 终端演示 / 标题 / 代码对比 / 投票）
2. **AI 配音** — Edge-TTS 驱动，支持中文语音，语速可调
3. **自动字幕** — 文案自动切分时间轴，生成 SRT 字幕
4. **合成视频** — FFmpeg 渲染，逐段合成，输出适配抖音的 9:16 竖屏 MP4

## 快速开始

```bash
# 安装
pip install clipgen

# 查看可用模板
clipgen templates

# 从配置生成视频
clipgen build examples/cursor_vs.yaml
```

## 配置格式

```yaml
output: "my_video.mp4"
voice: "zh-CN-XiaoxiaoNeural"   # TTS 语音
rate: "+30%"                     # 语速

scenes:
  - script: "文案内容，AI 会读出这段文字"
    template: title               # 标题模板
    data:
      title: "你的标题"
      subtitle: "副标题"
      accent: "#00d2ff"
      tags: ["🏷️ 标签1", "🏷️ 标签2"]

  - script: "第二段文案"
    template: terminal             # 终端模板
    data:
      title: "终端标题"
      lines:
        - text: "$ 命令"
          color: green
        - text: "  ✓ 输出"
          color: green
      note: "底部说明文字"

  - script: "最后一段..."
    template: cta                  # 关注引导模板
    data:
      text: "关注我"
      subtitle: "每天一个技巧"
```

## 内置模板

| 模板 | 说明 |
|------|------|
| `title` | 标题卡，带标签、网格背景 |
| `comparison` | 分屏对比（VS 风格） |
| `terminal` | 终端窗口，显示命令输出 |
| `code_diff` | Before/After 代码对比 |
| `question` | A/B 投票选择，引导评论 |
| `cta` | 关注引导，带按钮和装饰 |

## 示例

`examples/` 目录下有完整可运行的示例配置：

```bash
# Claude Code vs Cursor 对比视频
clipgen build examples/cursor_vs.yaml
```

生成的视频效果预览：

[![Demo](https://img.shields.io/badge/-%E6%92%AD%E6%94%BE%E9%A2%84%E8%A7%88-00d2ff)]()

## 依赖

- Python ≥ 3.10
- Pillow — 画面渲染
- edge-tts — AI 语音合成
- imageio-ffmpeg — ffmpeg 绑定
- PyYAML — 配置解析
- FFmpeg — 视频合成（由 imageio-ffmpeg 自动管理）

## 定制模板

模板是一个接受 `(draw: ImageDraw, scene: dict)` 的函数：

```python
# my_template.py
from clipgen.utils import *

def render(draw: ImageDraw, scene: dict):
    gradient_bg(draw)
    draw.text((100, 500), scene.get("text", "Hello"), fill=hex_rgb("#fff"), font=F(36))

# 注册
from clipgen.engine import register_template
register_template("my_template", render)
```

## 路线图

- [ ] 更多模板（代码编辑、对话气泡、数据图表）
- [ ] 多语言支持
- [ ] 画面过渡动画（非静态图）
- [ ] Web UI 配置界面
- [ ] 模板市场（社区贡献）

## License

MIT
