"""CLI entry point"""

import argparse
import sys
import os
import yaml

from .engine import build, register_template, TEMPLATE_REGISTRY
from . import __version__


def list_templates():
    from .engine import auto_import_templates
    auto_import_templates()
    print("Available templates:")
    for name in sorted(TEMPLATE_REGISTRY):
        print(f"  - {name}")


def auto_config(scripts, output="auto_video.mp4", voice="zh-CN-XiaoxiaoNeural", rate="+30%"):
    """Auto-generate a config from a list of script lines."""
    n = len(scripts)
    scenes = []

    for i, script in enumerate(scripts):
        if n == 1:
            tpl = "title"
            data = {"title": script[:20], "subtitle": "", "tags": ["AI 视频"]}
        elif i == 0:
            tpl = "title"
            title_text = script[:20] if len(script) > 20 else script
            data = {"title": title_text, "subtitle": "", "tags": ["AI 视频"]}
        elif i == n - 1:
            tpl = "cta"
            data = {"text": "关注我", "subtitle": "每天一个 AI 编程效率技巧", "button_text": "下期更精彩 →"}
        elif i == 1 and n > 2:
            tpl = "terminal"
            data = {
                "title": "自动生成",
                "accent": "#00d2ff",
                "lines": [
                    {"text": "$ clipgen build video.yaml", "color": "green"},
                    {"text": "  Building...", "color": "dim"},
                    {"text": "  [1/3] title       OK", "color": "cyan"},
                    {"text": "  [2/3] terminal    OK", "color": "cyan"},
                    {"text": "  [3/3] cta         OK", "color": "cyan"},
                    {"text": "  Done! → video.mp4", "color": "green"},
                ],
                "note": "一行命令，从文案到成品",
            }
        else:
            tpl = "terminal"
            data = {
                "title": f"场景 {i+1}",
                "accent": "#00d2ff",
                "lines": [
                    {"text": f"$ 步骤 {i+1}", "color": "green"},
                    {"text": f"  Processing...", "color": "dim"},
                    {"text": f"  ✓ Done", "color": "green"},
                ],
                "note": "",
            }

        scenes.append({"script": script, "template": tpl, "data": data})

    return {"output": output, "voice": voice, "rate": rate, "scenes": scenes}


def wizard_mode():
    """Interactive wizard for non-technical users."""
    print("\n==================== clipgen 视频生成向导 ====================\n")

    print("输入你的视频文案，每段话分开写。")
    print("输入空行结束。\n")

    scripts = []
    i = 1
    while True:
        line = input(f"  第 {i} 段文案: ").strip()
        if not line:
            if i > 1:
                break
            print("  至少需要一段文案")
            continue
        scripts.append(line)
        i += 1

    if not scripts:
        print("没有输入，退出")
        return

    print(f"\n  共 {len(scripts)} 段文案，将自动分配模板生成视频。")
    output = input(f"  输出文件名 [auto_video.mp4]: ").strip() or "auto_video.mp4"

    config = auto_config(scripts, output=output)
    _save_last_config(config)

    print(f"\n  开始生成视频...\n")

    try:
        out = build(config, verbose=True)
        print(f"\n  视频已保存到: {out}")
    except Exception as e:
        print(f"\n  生成失败: {e}")


def _save_last_config(config: dict):
    """Save config to user home dir so 'refine' can find it later."""
    config_dir = os.path.join(os.path.expanduser("~"), ".clipgen")
    os.makedirs(config_dir, exist_ok=True)
    path = os.path.join(config_dir, "last_config.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    return path


def _load_last_config():
    """Load the last saved config from ~/.clipgen/last_config.yaml."""
    path = os.path.join(os.path.expanduser("~"), ".clipgen", "last_config.yaml")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _prompt_template_data(template_name: str) -> dict:
    """Return default data fields for a given template."""
    defaults = {
        "title": {
            "title": "标题",
            "subtitle": "副标题",
            "accent": "#00d2ff",
            "tags": ["标签1", "标签2"],
        },
        "comparison": {
            "left": {"name": "方案A", "subtitle": "描述A", "color": "#58a6ff"},
            "right": {"name": "方案B", "subtitle": "描述B", "color": "#00d2ff"},
            "caption": "",
            "tags": [],
        },
        "terminal": {
            "title": "终端标题",
            "accent": "#00d2ff",
            "lines": [
                {"text": "$ 命令", "color": "green"},
                {"text": "  Done", "color": "dim"},
            ],
            "note": "提示文字",
        },
        "code_diff": {
            "title": "代码对比",
            "accent": "#00c853",
            "before": {"label": "Before", "lines": [{"text": "旧代码", "color": "#c9d1d9"}]},
            "after": {"label": "After", "lines": [{"text": "新代码", "color": "#c9d1d9"}]},
            "note": "",
        },
        "question": {
            "question": "你选哪个？",
            "option_a": "选项A",
            "option_b": "选项B",
            "a_color": "#58a6ff",
            "b_color": "#00d2ff",
            "comment_prompt": "评论区写下你的想法",
        },
        "cta": {
            "text": "关注我",
            "subtitle": "每天一个技巧",
            "button_text": "了解更多 →",
        },
    }
    return defaults.get(template_name, {})


def _edit_data_fields(data: dict, indent: str = "  "):
    """Interactively edit simple data fields. Returns True if anything changed."""
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
            # Skip complex types (list of dicts etc.)
            print(f"{indent}{k}: ({type(v).__name__}, {len(v)} 项 — 保存为 YAML 后可手动编辑)")
    return changed


def _edit_scene(config: dict, idx: int):
    """Interactively edit a single scene."""
    scene = config["scenes"][idx]
    templates = sorted(TEMPLATE_REGISTRY.keys()) if TEMPLATE_REGISTRY else []

    if not templates:
        from .engine import auto_import_templates
        auto_import_templates()
        templates = sorted(TEMPLATE_REGISTRY.keys())

    print(f"\n  ======== 场景 {idx + 1} ========\n")

    # --- Edit script ---
    print(f"  文案: {scene['script']}")
    new_script = input("  新文案 (直接回车保持不变): ").strip()
    if new_script:
        scene["script"] = new_script

    # --- Edit template ---
    print(f"\n  当前模板: {scene['template']}")
    print(f"  可选模板: {', '.join(templates)}")
    new_tpl = input("  新模板 (直接回车保持不变): ").strip()
    if new_tpl:
        if new_tpl in TEMPLATE_REGISTRY:
            old_tpl = scene["template"]
            scene["template"] = new_tpl
            if new_tpl != old_tpl:
                print(f"\n  → 模板已切换为 '{new_tpl}'，请设置画面参数：")
                scene["data"] = _prompt_template_data(new_tpl)
                _edit_data_fields(scene["data"])
                return
        else:
            print(f"  模板 '{new_tpl}' 不存在，保持原模板")

    # --- Edit data fields ---
    data = scene.get("data", {})
    if data:
        print(f"\n  画面参数 (直接回车保持不变):")
        _edit_data_fields(data)
    else:
        print(f"\n  该模板没有画面参数需要设置。")


def refine_mode():
    """Interactive video config refinement — modify and regenerate."""
    config = _load_last_config()
    if config is None:
        print("\n==================== clipgen 视频修改工具 ====================\n")
        print("  没有找到上一次的视频配置。")
        print()
        print("  请先通过以下命令生成一个视频：")
        print("    clipgen quick \"第一段\" \"第二段\" \"第三段\"")
        print("    或者")
        print("    clipgen wizard")
        print()
        return

    from .engine import auto_import_templates
    auto_import_templates()

    while True:
        scenes = config["scenes"]
        print("\n==================== clipgen 视频修改工具 ====================\n")
        print(f"  输出: {config.get('output', '?')}  |  配音: {config.get('voice', '?')}  |  语速: {config.get('rate', '?')}")
        print(f"\n  共 {len(scenes)} 个场景:\n")

        for i, sc in enumerate(scenes):
            txt = sc["script"][:55] + "..." if len(sc["script"]) > 55 else sc["script"]
            print(f"  [{i + 1}] {sc['template']:12s}  {txt}")

        print()
        print("  ┌──────────────────────────────────────────────────────────┐")
        print("  │  输入 1-{}   修改对应场景                                    │".format(len(scenes)))
        print("  │  v         查看所有场景完整内容                              │")
        print("  │  p         重新生成视频（用修改后的配置）                    │")
        print("  │  s         保存为 YAML 配置文件到当前目录                    │")
        print("  │  q         退出                                              │")
        print("  └──────────────────────────────────────────────────────────┘")
        print()

        choice = input("  你的选择 > ").strip()

        if choice == "q":
            print()
            break

        elif choice == "p":
            print()
            try:
                out = build(config, verbose=True)
                print(f"\n  ✅ 视频已更新: {out}")
            except Exception as e:
                print(f"\n  ❌ 生成失败: {e}")
            input("\n  按回车继续...")

        elif choice == "s":
            default_name = config.get("output", "video.yaml")
            if default_name.endswith(".mp4"):
                default_name = default_name.replace(".mp4", ".yaml")
            path = input(f"  保存到 [{default_name}]: ").strip() or default_name
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            print(f"  ✅ 已保存: {path}")
            input("\n  按回车继续...")

        elif choice == "v":
            print()
            for i, sc in enumerate(scenes):
                print(f"  ────── 场景 {i + 1} ──────")
                print(f"  模板: {sc['template']}")
                print(f"  文案: {sc['script']}")
                print(f"  数据: {yaml.dump(sc.get('data', {}), allow_unicode=True, default_flow_style=False).rstrip()}")
                print()
            input("  按回车继续...")

        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(scenes):
                _edit_scene(config, idx)
                _save_last_config(config)
                print(f"  ✅ 场景 {idx + 1} 已更新")
            else:
                print(f"  ❌ 请输入 1-{len(scenes)}")
        else:
            print("  ❌ 无效输入，请重新选择")

    # Save on exit
    _save_last_config(config)
    print("  配置已保存。下次运行 clipgen refine 可继续修改。\n")


_EPILOG = """
使用示例 (Examples):

  # 最简单方式 — 直接输入文案，自动生成视频
  clipgen quick "大家好" "今天介绍一个好用的工具" "关注我"

  # 交互式向导 — 一步步输入
  clipgen wizard

  # 修改上一次生成的视频（调整文案、换模板、改颜色，然后重新生成）
  clipgen refine

  # 从 YAML 配置文件生成（进阶用户）
  clipgen build my_video.yaml

入门步骤:
  1. clipgen quick "第一段话" "第二段话" "第三段话"    ← 快速生成第一个视频
  2. clipgen refine                                      ← 不满意？随时修改
  3. clipgen wizard                                      ← 或者试试交互式向导
"""


def main():
    parser = argparse.ArgumentParser(
        prog="clipgen",
        description="短视频自动生成工具 — AI 配音 + 字幕 + 画面，一键生成",
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"clipgen {__version__}")

    sub = parser.add_subparsers(dest="command", help="命令说明")

    # ── build ──
    bp = sub.add_parser("build", help="从 YAML 配置文件生成视频（进阶）")
    bp.add_argument("config", help="YAML 配置文件路径，参考 examples/ 目录下的示例")
    bp.add_argument("-o", "--output", help="指定输出视频文件名（覆盖配置中的设置）")
    bp.add_argument("-q", "--quiet", action="store_true", help="安静模式，不显示进度")

    # ── quick ──
    qp = sub.add_parser("quick", help="【推荐】最快捷的方式，直接输入文案生成视频")
    qp.add_argument(
        "scripts", nargs="+",
        help="视频文案，每段话作为一个单独的参数。第一段自动做标题，最后一段做关注引导，中间的做内容演示。"
            "示例: clipgen quick \"大家好\" \"今天聊AI\" \"关注我\""
    )
    qp.add_argument("-o", "--output", default="quick_video.mp4", help="输出视频文件名 [默认: quick_video.mp4]")
    qp.add_argument("-q", "--quiet", action="store_true", help="安静模式，不显示进度")

    # ── wizard ──
    sub.add_parser("wizard", help="【推荐】交互式向导，一步步输入文案生成视频")

    # ── refine ──
    rp = sub.add_parser("refine", help="【推荐】修改上一次生成的视频（改文案、换模板、调颜色、重新生成）")
    rp.add_argument("-p", "--preview", action="store_true",
                    help="直接重新生成，不进入交互修改界面（快速预览最新改动）")

    # ── templates ──
    sub.add_parser("templates", help="查看所有可用的画面模板列表")

    args = parser.parse_args()

    # ── build ──
    if args.command == "build":
        with open(args.config, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        if args.output:
            config["output"] = args.output
        _save_last_config(config)
        try:
            out = build(config, verbose=not args.quiet)
            if not args.quiet:
                print(f"\n  视频已保存到: {out}")
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)

    # ── quick ──
    elif args.command == "quick":
        config = auto_config(args.scripts, output=args.output)
        _save_last_config(config)
        print(f"  共 {len(config['scenes'])} 个场景，开始生成...\n")
        try:
            out = build(config, verbose=not args.quiet)
            if not args.quiet:
                print(f"\n  视频已保存到: {out}")
                print("  提示: 运行 clipgen refine 可继续修改这个视频")
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)

    # ── wizard ──
    elif args.command == "wizard":
        wizard_mode()

    # ── refine ──
    elif args.command == "refine":
        if args.preview:
            config = _load_last_config()
            if config is None:
                print("没有找到上一次的配置，请先运行 clipgen quick 或 clipgen wizard")
                sys.exit(1)
            try:
                out = build(config, verbose=True)
                print(f"\n  视频已保存到: {out}")
            except Exception as e:
                print(f"错误: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            refine_mode()

    # ── templates ──
    elif args.command == "templates":
        list_templates()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
