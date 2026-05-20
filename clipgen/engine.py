"""Core engine: orchestrate slide generation, audio, subtitles, and rendering."""

import os
import shutil
import tempfile
from PIL import ImageDraw

from .utils import W, H, new_image, save_slide
from .audio import generate_audio_sync
from .subtitles import write_srt
from .render import render_segment, concat_segments, get_ffmpeg

TEMPLATE_REGISTRY = {}


def register_template(name: str, render_fn):
    TEMPLATE_REGISTRY[name] = render_fn


def auto_import_templates():
    """Lazy-import all built-in templates."""
    import importlib
    import pkgutil
    import clipgen.templates
    for importer, modname, ispkg in pkgutil.iter_modules(clipgen.templates.__path__):
        if modname.startswith("_"):
            continue
        mod = importlib.import_module(f"clipgen.templates.{modname}")
        if hasattr(mod, "render"):
            register_template(getattr(mod, "TEMPLATE_NAME", modname), mod.render)


def validate_config(config: dict) -> list:
    """Validate a config dict and return list of errors."""
    errors = []
    if "scenes" not in config or not isinstance(config["scenes"], list):
        errors.append("Missing or invalid 'scenes' list")
    else:
        for i, scene in enumerate(config["scenes"]):
            if "script" not in scene:
                errors.append(f"Scene[{i}]: missing 'script'")
            if "template" not in scene:
                errors.append(f"Scene[{i}]: missing 'template'")
    return errors


def build(config: dict, work_dir: str = None, verbose: bool = True):
    """Build a video from a config dict.

    Args:
        config: Parsed YAML config dict
        work_dir: Working directory for intermediate files. Auto-created if None.
        verbose: Print progress messages

    Returns:
        Path to the final video file.
    """
    auto_import_templates()

    own_workdir = work_dir is None
    if work_dir is None:
        work_dir = tempfile.mkdtemp(prefix="clipgen_")

    errors = validate_config(config)
    if errors:
        raise ValueError("\n".join(errors))

    output_path = os.path.abspath(config.get("output", "output.mp4"))
    voice = config.get("voice", "zh-CN-XiaoxiaoNeural")
    rate = config.get("rate", "+30%")
    scenes = config["scenes"]

    segment_paths = []
    audio_durs = []

    if verbose:
        print(f"  Building {len(scenes)} scenes...")

    for i, scene in enumerate(scenes):
        prefix = f"scene_{i:03d}"

        # --- Slide ---
        img = new_image()
        draw = ImageDraw.Draw(img)
        tpl_name = scene["template"]
        tpl_fn = TEMPLATE_REGISTRY.get(tpl_name)
        if tpl_fn is None:
            raise ValueError(f"Unknown template '{tpl_name}'. Available: {list(TEMPLATE_REGISTRY.keys())}")

        tpl_fn(draw, scene.get("data", {}))
        slide_path = os.path.join(work_dir, f"{prefix}.png")
        save_slide(img, slide_path)

        # --- Audio ---
        audio_path = os.path.join(work_dir, f"{prefix}.mp3")
        dur = generate_audio_sync(scene["script"], audio_path, voice, rate)
        audio_durs.append(dur)

        # --- Subtitles ---
        srt_path = os.path.join(work_dir, f"{prefix}.srt")
        write_srt(scene["script"], dur, srt_path)

        # --- Segment ---
        seg_path = os.path.join(work_dir, f"{prefix}.ts")
        ok = render_segment(get_ffmpeg(), slide_path, audio_path, srt_path, seg_path)
        if not ok:
            raise RuntimeError(f"Segment {i} render failed")
        segment_paths.append(seg_path)

        if verbose:
            print(f"  [{i+1}/{len(scenes)}] {dur:.1f}s — {tpl_name}")

    # --- Concatenate ---
    if verbose:
        print(f"  Merging {len(segment_paths)} segments...")
    ok = concat_segments(get_ffmpeg(), segment_paths, output_path)
    if not ok:
        raise RuntimeError("Concatenation failed")

    # --- Cleanup ---
    for p in segment_paths:
        try: os.remove(p)
        except: pass
    if own_workdir:
        try: shutil.rmtree(work_dir)
        except: pass

    total = sum(audio_durs)
    mb = os.path.getsize(output_path) / 1024 / 1024

    if verbose:
        print(f"\n  Done!")
        print(f"  Output: {output_path}")
        print(f"  Size:   {mb:.1f}MB")
        print(f"  Duration: {total:.0f}s")

    return output_path
