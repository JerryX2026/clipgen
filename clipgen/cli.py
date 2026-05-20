"""CLI entry point"""

import argparse
import sys
import os
import re
import yaml

from .engine import build, register_template, TEMPLATE_REGISTRY
from . import __version__


# ── helpers ──

def _guess_lang(scripts):
    """Return 'zh' if any script contains Chinese chars, else 'en'."""
    return 'zh' if any(re.search(r'[一-鿿]', s) for s in scripts) else 'en'


_DEFAULT_VOICE = {
    'zh': 'zh-CN-XiaoxiaoNeural',
    'en': 'en-US-AriaNeural',
}


def list_templates():
    from .engine import auto_import_templates
    auto_import_templates()
    print("Available templates / 可用模板:")
    for name in sorted(TEMPLATE_REGISTRY):
        print(f"  - {name}")


def auto_config(scripts, output="auto_video.mp4", voice=None, rate="+30%"):
    """Auto-generate a config from a list of script lines (bilingual)."""
    lang = _guess_lang(scripts)
    n = len(scripts)
    scenes = []

    if voice is None:
        voice = _DEFAULT_VOICE[lang]

    for i, script in enumerate(scripts):
        if lang == 'zh':
            scenes.append(_make_zh_scene(script, i, n))
        else:
            scenes.append(_make_en_scene(script, i, n))

    return {"output": output, "voice": voice, "rate": rate, "scenes": scenes}


def _make_zh_scene(script, i, n):
    if n == 1:
        return {"script": script, "template": "title", "data": {
            "title": script[:20], "subtitle": "", "tags": ["AI 视频"]}}
    if i == 0:
        return {"script": script, "template": "title", "data": {
            "title": script[:20] if len(script) > 20 else script,
            "subtitle": "", "tags": ["AI 视频"]}}
    if i == n - 1:
        return {"script": script, "template": "cta", "data": {
            "text": "关注我", "subtitle": "每天一个 AI 编程效率技巧",
            "button_text": "下期更精彩 →"}}
    if i == 1 and n > 2:
        return {"script": script, "template": "terminal", "data": {
            "title": "自动生成", "accent": "#00d2ff",
            "lines": [
                {"text": "$ clipgen build video.yaml", "color": "green"},
                {"text": "  Building...", "color": "dim"},
                {"text": "  [1/3] title       OK", "color": "cyan"},
                {"text": "  [2/3] terminal    OK", "color": "cyan"},
                {"text": "  [3/3] cta         OK", "color": "cyan"},
                {"text": "  Done! → video.mp4", "color": "green"}],
            "note": "一行命令，从文案到成品"}}
    return {"script": script, "template": "terminal", "data": {
        "title": f"场景 {i+1}", "accent": "#00d2ff",
        "lines": [
            {"text": f"$ 步骤 {i+1}", "color": "green"},
            {"text": "  Processing...", "color": "dim"},
            {"text": "  ✓ Done", "color": "green"}],
        "note": ""}}


def _make_en_scene(script, i, n):
    if n == 1:
        return {"script": script, "template": "title", "data": {
            "title": script[:25], "subtitle": "", "tags": ["AI Video"]}}
    if i == 0:
        return {"script": script, "template": "title", "data": {
            "title": script[:25] if len(script) > 25 else script,
            "subtitle": "", "tags": ["AI Video"]}}
    if i == n - 1:
        return {"script": script, "template": "cta", "data": {
            "text": "Follow Me", "subtitle": "Daily AI coding tips",
            "button_text": "See More →"}}
    if i == 1 and n > 2:
        return {"script": script, "template": "terminal", "data": {
            "title": "Auto Generate", "accent": "#00d2ff",
            "lines": [
                {"text": "$ clipgen build video.yaml", "color": "green"},
                {"text": "  Building...", "color": "dim"},
                {"text": "  [1/3] title       OK", "color": "cyan"},
                {"text": "  [2/3] terminal    OK", "color": "cyan"},
                {"text": "  [3/3] cta         OK", "color": "cyan"},
                {"text": "  Done! → video.mp4", "color": "green"}],
            "note": "One command, from script to video"}}
    return {"script": script, "template": "terminal", "data": {
        "title": f"Step {i+1}", "accent": "#00d2ff",
        "lines": [
            {"text": f"$ step {i+1}", "color": "green"},
            {"text": "  Processing...", "color": "dim"},
            {"text": "  ✓ Done", "color": "green"}],
        "note": ""}}


# ── wizard ──

_WIZARD_PROMPTS = {
    'zh': {
        'header': "clipgen 视频生成向导",
        'desc': "输入你的视频文案，每段话分开写。输入空行结束。",
        'script': "第 {} 段文案",
        'need_one': "至少需要一段文案",
        'no_input': "没有输入，退出",
        'count': "共 {} 段文案，将自动分配模板生成视频。",
        'output': "输出文件名 [auto_video.mp4]",
        'start': "开始生成视频...",
        'done': "视频已保存到: {}",
        'fail': "生成失败: {}",
    },
    'en': {
        'header': "clipgen Video Wizard",
        'desc': "Type your video script, one paragraph at a time. Leave a blank line to finish.",
        'script': "Paragraph {}",
        'need_one': "At least one paragraph is required",
        'no_input': "No input, exiting",
        'count': "{} paragraphs, will auto-assign templates.",
        'output': "Output filename [auto_video.mp4]",
        'start': "Generating video...",
        'done': "Video saved to: {}",
        'fail': "Generation failed: {}",
    },
}


def wizard_mode():
    """Interactive wizard — bilingual."""
    # Detect language from first input
    scripts = []
    lang = 'zh'

    print(f"\n{'='*20} clipgen {'='*20}\n")

    for l in ['zh', 'en']:
        txt = _WIZARD_PROMPTS[l]['desc']
        if l == 'zh':
            print(f"  {txt}")
        else:
            print(f"  {txt}")

    i = 1
    while True:
        line = input(f"  {i}: ").strip()
        if not line:
            if i > 1:
                break
            print(f"  {_WIZARD_PROMPTS['zh']['need_one']} / {_WIZARD_PROMPTS['en']['need_one']}")
            continue
        scripts.append(line)
        i += 1

    if not scripts:
        print(f"  {_WIZARD_PROMPTS['zh']['no_input']} / {_WIZARD_PROMPTS['en']['no_input']}")
        return

    # Detect language from actual input
    lang = _guess_lang(scripts)
    prompts = _WIZARD_PROMPTS[lang]

    print(f"\n  {prompts['count'].format(len(scripts))}")
    output = input(f"  {prompts['output']}: ").strip() or "auto_video.mp4"

    config = auto_config(scripts, output=output)
    _save_last_config(config)

    print(f"\n  {prompts['start']}\n")

    try:
        out = build(config, verbose=True)
        print(f"\n  {prompts['done'].format(out)}")
    except Exception as e:
        print(f"\n  {prompts['fail'].format(e)}")


# ── config persistence ──

def _save_last_config(config: dict):
    config_dir = os.path.join(os.path.expanduser("~"), ".clipgen")
    os.makedirs(config_dir, exist_ok=True)
    path = os.path.join(config_dir, "last_config.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    return path


def _load_last_config():
    path = os.path.join(os.path.expanduser("~"), ".clipgen", "last_config.yaml")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── refine helpers ──

_TEMPLATE_DEFAULTS = {
    'zh': {
        "title": {"title": "标题", "subtitle": "副标题", "accent": "#00d2ff", "tags": ["标签1", "标签2"]},
        "comparison": {
            "left": {"name": "方案A", "subtitle": "描述A", "color": "#58a6ff"},
            "right": {"name": "方案B", "subtitle": "描述B", "color": "#00d2ff"},
            "caption": "", "tags": []},
        "terminal": {
            "title": "终端标题", "accent": "#00d2ff",
            "lines": [{"text": "$ 命令", "color": "green"}, {"text": "  Done", "color": "dim"}],
            "note": "提示文字"},
        "code_diff": {
            "title": "代码对比", "accent": "#00c853",
            "before": {"label": "Before", "lines": [{"text": "旧代码", "color": "#c9d1d9"}]},
            "after": {"label": "After", "lines": [{"text": "新代码", "color": "#c9d1d9"}]},
            "note": ""},
        "question": {
            "question": "你选哪个？", "option_a": "选项A", "option_b": "选项B",
            "a_color": "#58a6ff", "b_color": "#00d2ff", "comment_prompt": "评论区写下你的想法"},
        "cta": {"text": "关注我", "subtitle": "每天一个技巧", "button_text": "了解更多 →"},
    },
    'en': {
        "title": {"title": "Title", "subtitle": "Subtitle", "accent": "#00d2ff", "tags": ["Tag 1", "Tag 2"]},
        "comparison": {
            "left": {"name": "Option A", "subtitle": "Description A", "color": "#58a6ff"},
            "right": {"name": "Option B", "subtitle": "Description B", "color": "#00d2ff"},
            "caption": "", "tags": []},
        "terminal": {
            "title": "Terminal", "accent": "#00d2ff",
            "lines": [{"text": "$ command", "color": "green"}, {"text": "  Done", "color": "dim"}],
            "note": "Hint text"},
        "code_diff": {
            "title": "Code Diff", "accent": "#00c853",
            "before": {"label": "Before", "lines": [{"text": "old code", "color": "#c9d1d9"}]},
            "after": {"label": "After", "lines": [{"text": "new code", "color": "#c9d1d9"}]},
            "note": ""},
        "question": {
            "question": "What do you choose?", "option_a": "Option A", "option_b": "Option B",
            "a_color": "#58a6ff", "b_color": "#00d2ff", "comment_prompt": "💬 Comment below"},
        "cta": {"text": "Follow Me", "subtitle": "Daily tips", "button_text": "Learn More →"},
    },
}


def _prompt_template_data(template_name: str, lang='zh') -> dict:
    defaults = _TEMPLATE_DEFAULTS.get(lang, _TEMPLATE_DEFAULTS['zh'])
    # Make a deep-ish copy so mutations don't affect the cached dicts
    import copy
    return copy.deepcopy(defaults.get(template_name, {}))


def _edit_data_fields(data: dict, indent: str = "  "):
    changed = False
    for k, v in data.items():
        if isinstance(v, str):
            new = input(f"{indent}{k} [{v}]: ").strip()
            if new:
                data[k] = new
                changed = True
        elif isinstance(v, list) and all(isinstance(x, str) for x in v):
            current = ", ".join(v)
            new = input(f"{indent}{k} [{current}]: ").strip()
            if new:
                data[k] = [x.strip() for x in new.split(",") if x.strip()]
                changed = True
        elif isinstance(v, dict):
            print(f"{indent}{k}:")
            if _edit_data_fields(v, indent + "  "):
                changed = True
        else:
            print(f"{indent}{k}: ({type(v).__name__}, {len(v)} items — edit YAML for details)")
    return changed


def _edit_scene(config: dict, idx: int):
    scene = config["scenes"][idx]
    templates = sorted(TEMPLATE_REGISTRY.keys()) if TEMPLATE_REGISTRY else []

    if not templates:
        from .engine import auto_import_templates
        auto_import_templates()
        templates = sorted(TEMPLATE_REGISTRY.keys())

    lang = _guess_lang([scene["script"]])
    prompts = {
        'zh': {"scene": "场景", "script": "文案", "keep": "直接回车保持不变",
               "template": "当前模板", "options": "可选模板", "data": "画面参数",
               "switched": "模板已切换为", "set_data": "请设置画面参数："},
        'en': {"scene": "Scene", "script": "Script", "keep": "leave blank to keep",
               "template": "Current template", "options": "Available templates", "data": "Scene data",
               "switched": "Switched to template", "set_data": "Set scene data:"},
    }
    p = prompts[lang]

    print(f"\n  ======== {p['scene']} {idx + 1} ========\n")
    print(f"  {p['script']}: {scene['script']}")
    new_script = input(f"  New {p['script']} ({p['keep']}): ").strip()
    if new_script:
        scene["script"] = new_script
        # Re-detect lang after script change
        lang = _guess_lang([scene["script"]])
        p = prompts[lang]

    print(f"\n  {p['template']}: {scene['template']}")
    print(f"  {p['options']}: {', '.join(templates)}")
    new_tpl = input(f"  New template ({p['keep']}): ").strip()
    if new_tpl:
        if new_tpl in TEMPLATE_REGISTRY:
            old_tpl = scene["template"]
            scene["template"] = new_tpl
            if new_tpl != old_tpl:
                print(f"\n  → {p['switched']} '{new_tpl}'，{p['set_data']}")
                scene["data"] = _prompt_template_data(new_tpl, lang)
                _edit_data_fields(scene["data"])
                return
        else:
            print(f"  Template '{new_tpl}' not found, keeping current")

    data = scene.get("data", {})
    if data:
        print(f"\n  {p['data']} ({p['keep']}):")
        _edit_data_fields(data)
    else:
        print(f"\n  No data fields for this template.")


def refine_mode():
    """Interactive video config refinement — bilingual."""
    config = _load_last_config()
    if config is None:
        print("\n" + "=" * 20 + " clipgen " + "=" * 20)
        print("\n  No previous config found.")
        print("  Please generate a video first:")
        print("    clipgen quick \"script 1\" \"script 2\" \"script 3\"")
        print("    clipgen wizard")
        return

    from .engine import auto_import_templates
    auto_import_templates()

    while True:
        scenes = config["scenes"]
        print("\n" + "=" * 20 + " clipgen " + "=" * 20 + "\n")
        print(f"  Output: {config.get('output', '?')}  |  Voice: {config.get('voice', '?')}  |  Rate: {config.get('rate', '?')}")
        print(f"  {len(scenes)} scene(s):\n")

        for i, sc in enumerate(scenes):
            txt = sc["script"][:55] + "..." if len(sc["script"]) > 55 else sc["script"]
            print(f"  [{i + 1}] {sc['template']:12s}  {txt}")

        print()
        print("  ┌───────────────────────────────────────────────────────────┐")
        print("  │  1-{}   Edit scene                                        │".format(str(len(scenes)).ljust(3)))
        print("  │  v     View all scenes (查看所有场景)                      │")
        print("  │  p     Preview / regenerate (重新生成)                     │")
        print("  │  s     Save config as YAML (保存配置)                      │")
        print("  │  q     Quit (退出)                                        │")
        print("  └───────────────────────────────────────────────────────────┘")

        choice = input("\n  Your choice > ").strip()

        if choice == "q":
            break
        elif choice == "p":
            print()
            try:
                out = build(config, verbose=True)
                print(f"\n  ✅ Video saved: {out}")
            except Exception as e:
                print(f"\n  ❌ Error: {e}")
            input("\n  Press Enter to continue...")
        elif choice == "s":
            default_name = config.get("output", "video.yaml")
            if default_name.endswith(".mp4"):
                default_name = default_name.replace(".mp4", ".yaml")
            path = input(f"  Save as [{default_name}]: ").strip() or default_name
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            print(f"  ✅ Saved: {path}")
            input("\n  Press Enter to continue...")
        elif choice == "v":
            print()
            for i, sc in enumerate(scenes):
                print(f"  ── Scene {i + 1} ──")
                print(f"  Template: {sc['template']}")
                print(f"  Script: {sc['script']}")
                print(f"  Data: {yaml.dump(sc.get('data', {}), allow_unicode=True, default_flow_style=False).rstrip()}")
            input("\n  Press Enter to continue...")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(scenes):
                _edit_scene(config, idx)
                _save_last_config(config)
                print(f"  ✅ Scene {idx + 1} updated")
            else:
                print(f"  ❌ Enter 1-{len(scenes)}")
        else:
            print("  ❌ Invalid choice")

    _save_last_config(config)
    print("  Config saved. Run 'clipgen refine' again to continue editing.\n")


# ── CLI ──

_EPILOG = """
Examples / 使用示例:

  # English
  clipgen quick "Hey guys" "Today I want to share" "Follow me"
  clipgen wizard
  clipgen refine

  # Chinese / 中文
  clipgen quick "大家好" "今天介绍一个好用的工具" "关注我"
  clipgen wizard
  clipgen refine

  # Advanced / 进阶
  clipgen build my_video.yaml

Quick start / 快速开始:
  1. clipgen quick "script 1" "script 2" "script 3"    ← generate a video
  2. clipgen refine                                      ← not happy? modify it
  3. clipgen wizard                                      ← or try the interactive wizard
"""


def main():
    parser = argparse.ArgumentParser(
        prog="clipgen",
        description="短视频自动生成工具 / Short video auto generator — AI 配音+字幕+画面，一键生成",
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"clipgen {__version__}")

    sub = parser.add_subparsers(dest="command", help="Commands")

    bp = sub.add_parser("build", help="从 YAML 配置文件生成视频 / Build from YAML config")
    bp.add_argument("config", help="YAML 配置文件路径 / path to YAML config")
    bp.add_argument("-o", "--output", help="指定输出文件名 / override output path")
    bp.add_argument("-q", "--quiet", action="store_true", help="安静模式 / suppress output")

    qp = sub.add_parser("quick", help="直接输入文案生成视频 / Quick generate from script lines")
    qp.add_argument(
        "scripts", nargs="+",
        help="文案（每段一个参数）/ script lines, auto-detect English/Chinese."
    )
    qp.add_argument("-o", "--output", default="quick_video.mp4", help="输出文件名 [default: quick_video.mp4]")
    qp.add_argument("-q", "--quiet", action="store_true", help="安静模式 / suppress output")

    sub.add_parser("wizard", help="交互式向导 / Interactive wizard")

    rp = sub.add_parser("refine", help="修改上一次生成的视频 / Modify the last video config")
    rp.add_argument("-p", "--preview", action="store_true",
                    help="直接重新生成 / Regenerate without interactive editing")

    sub.add_parser("templates", help="查看可用模板 / List available templates")

    args = parser.parse_args()

    if args.command == "build":
        with open(args.config, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        if args.output:
            config["output"] = args.output
        _save_last_config(config)
        try:
            out = build(config, verbose=not args.quiet)
            if not args.quiet:
                print(f"\n  ✅ {'视频已保存' if _guess_lang([' ']) == 'zh' else 'Saved to'}: {out}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "quick":
        config = auto_config(args.scripts, output=args.output)
        _save_last_config(config)
        lang = _guess_lang(args.scripts)
        msg = f"  {len(config['scenes'])} 个场景，开始生成...\n" if lang == 'zh' else f"  {len(config['scenes'])} scenes, generating...\n"
        print(msg)
        try:
            out = build(config, verbose=not args.quiet)
            if not args.quiet:
                tag = "视频已保存到" if lang == 'zh' else "Video saved to"
                print(f"\n  ✅ {tag}: {out}")
                hint = "提示: 运行 clipgen refine 可继续修改" if lang == 'zh' else "Tip: run 'clipgen refine' to modify"
                print(f"  {hint}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "wizard":
        wizard_mode()

    elif args.command == "refine":
        if args.preview:
            config = _load_last_config()
            if config is None:
                print("No previous config found. Run 'clipgen quick' or 'clipgen wizard' first.")
                sys.exit(1)
            try:
                out = build(config, verbose=True)
                print(f"\n  ✅ Video saved: {out}")
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            refine_mode()

    elif args.command == "templates":
        list_templates()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
