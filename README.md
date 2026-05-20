# clipgen — 短视频自动生成器

> AI 配音 + 字幕 + 画面，一键生成短视频。**不需要 API Key，不消耗 token，完全免费。**

```bash
pip install clipgen
clipgen quick "大家好" "今天聊聊AI" "关注我"    # 三句话生成一个视频
```

<p align="center">
  <img src="demo_collage.jpg" alt="clipgen demo" width="540">
</p>

---

## 快速上手（小白版）

**不需要写任何配置文件，三步出视频：**

### 方式一：一句话命令

```bash
clipgen quick "大家好" "今天介绍一个开源工具" "一行命令生成短视频" "关注我"
```
第一句自动做标题，最后一句做关注引导，中间的做内容演示。直接出视频。

### 方式二：互动向导

```bash
clipgen wizard
```
一步步输入文案，系统自动分配模板，适合不想记命令的人。

### 方式三：不满意？修改它

```bash
clipgen refine
```
修改上一次生成的视频——换文案、换模板、调颜色，改完重新生成，反复调整直到满意。

---

## 它能做什么

1. **生成画面** — 6 套 Douyin 风格模板（标题 / 对比 / 终端演示 / 代码对比 / 投票 / 关注引导）
2. **AI 配音** — Edge-TTS 驱动，支持中文语音，语速可调，**完全免费**
3. **自动字幕** — 文案自动切分时间轴，生成 SRT 字幕
4. **合成视频** — FFmpeg 渲染，逐段合成，输出 9:16 竖屏 MP4

## 更多用法

```bash
# 查看可用模板
clipgen templates

# 从 YAML 配置文件生成（进阶）
clipgen build my_video.yaml

# 查看完整帮助
clipgen --help
```

## 示例配置（进阶用户）

```yaml
output: "my_video.mp4"
voice: "zh-CN-XiaoxiaoNeural"
rate: "+30%"

scenes:
  - script: "文案内容"
    template: title
    data:
      title: "你的标题"
      subtitle: "副标题"
      accent: "#00d2ff"
      tags: ["标签1", "标签2"]

  - script: "第二段文案"
    template: terminal
    data:
      title: "终端标题"
      accent: "#00d2ff"
      lines:
        - text: "$ 命令"
          color: green
        - text: "  ✓ Done"
          color: green

  - script: "关注我"
    template: cta
    data:
      text: "关注我"
      subtitle: "每天一个技巧"
```

## 内置模板

| 模板 | 说明 |
|------|------|
| `title` | 标题卡，网格背景 + 标签 |
| `comparison` | 分屏对比（VS 风格） |
| `terminal` | 终端窗口，命令输出演示 |
| `code_diff` | Before/After 代码对比 |
| `question` | A/B 投票选择，引导评论 |
| `cta` | 关注引导 + 按钮 |

## 定制模板

模板是一个 `(draw: ImageDraw, scene: dict)` 函数：

```python
from clipgen.utils import *
from clipgen.engine import register_template

def render(draw, scene):
    gradient_bg(draw)
    draw.text((100, 500), scene.get("text"), fill=hex_rgb("#fff"), font=F(36))

register_template("my_template", render)
```

注册后即可在命令中直接使用 `template: my_template`。

## 依赖

- Python ≥ 3.10
- Pillow, PyYAML, edge-tts, imageio-ffmpeg
- **不需要任何 API Key，不消耗 token，完全免费运行**

## License

MIT
