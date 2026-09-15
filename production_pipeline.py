#!/usr/bin/env python3
"""Generate a 10 x 32 ASMR storyboard, images, ZIP archive, and local dashboard.

Run once with --dry-run to inspect the generated JSON and dashboard without API calls.
Run with OPENAI_API_KEY set to generate the actual PNG files.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLIPS = [
    ("01", "Glass_Strawberry", "a translucent ruby-red glass strawberry with raised seeds"),
    ("02", "Glass_Orange", "a translucent amber glass orange with segmented interior detail"),
    ("03", "Glass_Kiwi", "a translucent emerald glass kiwi with a pale radial core and black seeds"),
    ("04", "Glass_Watermelon", "a translucent pink-and-green glass watermelon wedge with dark seeds"),
    ("05", "Glass_Grape", "a translucent violet glass grape cluster, cut one grape at a time"),
    ("06", "Hard_Gold_Bar", "a dense 24-karat gold bar with a brushed finish and serial engraving"),
    ("07", "Hard_Gold_Ingot", "a compact cast gold ingot with rounded corners"),
    ("08", "Hard_Gold_Coin_Stack", "a stack of thick solid-gold coins with reeded edges"),
    ("09", "Hard_Gold_Prism", "a polished hard-gold rectangular prism with beveled edges"),
    ("10", "Hard_Gold_Nugget", "a refined hard-gold nugget with a faceted mineral surface"),
]

GLOBAL_CONTINUITY = (
    "Same anonymous craftsperson; matte-black nitrile gloves only, no face. "
    "Matte charcoal cutting mat on a black slate workbench; stainless magnetic tool rest at frame right. "
    "One soft 5600K key from upper left, subtle cool fill, dark controlled background, no logos."
)

SYSTEM_PROMPT = """You are a meticulous ASMR video production director. Return only valid JSON.
Generate exactly 32 scenes S01 through S32. Each scene must contain sceneId, actionAndContinuity,
cameraShot, imagePrompt, and videoGenPrompt. The action must progress plausibly from setup,
controlled scoring/cutting, separation, arranging pieces, to a hero finish. Preserve hands, tool,
set, and lighting. Prompts must be in English. Do not include a face, brand, unsafe behaviour,
melting, impossible material physics, or on-screen text."""


def fallback_scenes(subject: str) -> list[dict[str, str]]:
    beats = [
        ("Place the subject on the center mark; both gloved hands enter from the lower frame.", "Wide establish, 45-degree front"),
        ("Left hand steadies the subject while the right aligns a precision cutting tool.", "Top-down macro"),
        ("The cutting edge touches the near edge without movement.", "Extreme close-up, side profile"),
        ("Make a shallow, controlled first score across the near third.", "Top-down close-up"),
        ("Continue the first score through the center in one slow stroke.", "Side macro tracking"),
        ("Finish the first score at the far edge and lift the tool vertically.", "Top-down close-up"),
        ("Position a slim guide in the score with tweezers.", "Macro 45-degree"),
        ("Apply balanced pressure so a clean separation line appears.", "Extreme close-up, side"),
        ("Return the cutting tool to its original grip and alignment.", "POV close-up"),
        ("Begin a perpendicular second score from the near edge.", "Top-down macro"),
        ("Advance the second score in a smooth, centered pass.", "Macro side tracking"),
        ("Cross the first score exactly at the center mark.", "Extreme close-up, top-down"),
        ("Complete the second score; pieces still retain their original outline.", "Top-down close-up"),
        ("Set the tool on the magnetic rest at frame right.", "Close-up, 45-degree"),
        ("Apply gentle, balanced outward pressure at the scored edges.", "Top-down macro"),
        ("The first segment releases and settles naturally onto the mat.", "Ultra macro, side"),
        ("Nudge the released segment two centimeters aside with a silicone-tipped tool.", "Top-down close-up"),
        ("Rotate the remaining piece 90 degrees while preserving the center mark.", "Overhead close-up"),
        ("Begin a third controlled score on the rotated face.", "Macro 3/4 angle"),
        ("Deepen the third score in one continuous pass.", "Side macro tracking"),
        ("Pause to show the crisp score and intact material texture.", "Extreme close-up"),
        ("Use the narrow guide with a gentle press along the score.", "POV macro"),
        ("A second segment releases with physically plausible resistance.", "Ultra macro, side"),
        ("Arrange the separated segments into a tidy fan with tweezers.", "Top-down close-up"),
        ("Align the largest remaining piece for a finishing pass.", "Macro side profile"),
        ("Make one small finishing cut with restrained pressure.", "Macro side profile"),
        ("The final small segment separates and settles without a jump cut.", "Extreme close-up, slow motion"),
        ("Brush tiny particles into a controlled line; keep tools at frame right.", "Top-down macro"),
        ("Refine the symmetrical display of completed pieces.", "Top-down hero shot"),
        ("Hold on the material textures and controlled reflections.", "Locked-off macro hero"),
        ("Hands withdraw slowly while the arranged pieces remain centered.", "Wide macro hero"),
        ("A slow light sweep reveals the finished display and clean workspace.", "Locked-off macro hero"),
    ]
    output = []
    for index, (action, shot) in enumerate(beats, 1):
        scene_id = f"S{index:02d}"
        image = (
            f"Photorealistic high-resolution ASMR craft still, {shot.lower()}, {subject}. {action} "
            f"{GLOBAL_CONTINUITY} 16:9, physically accurate reflections, micro-surface detail, shallow depth of field."
        )
        output.append({
            "sceneId": scene_id,
            "actionAndContinuity": f"{action} Subject: {subject}. {GLOBAL_CONTINUITY}",
            "cameraShot": shot,
            "imagePrompt": image,
            "videoGenPrompt": (
                f"Animate this {scene_id} at measured ASMR speed for 0.35 seconds: {action} "
                "Maintain exact hand position, set layout, and key light from the prior shot. "
                "Natural gravity and realistic rigid-material physics; no camera shake, morphing, extra fingers, or text."
            ),
        })
    return output


def parse_json(text: str) -> Any:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("LLM did not return a JSON object")
    return json.loads(match.group(0))


def make_clip_with_llm(client: Any, llm_model: str, number: str, title: str, subject: str) -> dict[str, Any]:
    request = f"""Create Clip_{number}_{title}. Subject: {subject}.\n{GLOBAL_CONTINUITY}\n
Return {{\"scenes\":[...]}} only. It must contain exactly 32 ordered scenes S01–S32."""
    response = client.responses.create(model=llm_model, instructions=SYSTEM_PROMPT, input=request)
    payload = parse_json(response.output_text)
    scenes = payload.get("scenes", [])
    expected = [f"S{i:02d}" for i in range(1, 33)]
    if [item.get("sceneId") for item in scenes] != expected:
        raise ValueError(f"Clip {number}: LLM response did not contain an ordered S01–S32 sequence")
    return build_clip(number, title, subject, scenes, source="llm")


def build_clip(number: str, title: str, subject: str, scenes: list[dict[str, str]], source: str) -> dict[str, Any]:
    for scene in scenes:
        scene["imageFile"] = f"{scene['sceneId']}.png"
    return {
        "clipId": f"Clip_{number}_{title}", "title": title.replace("_", " "),
        "folder": f"Clip_{number}", "subject": subject, "status": "planned",
        "sceneSource": source, "scenes": scenes,
    }


def make_project(args: argparse.Namespace, client: Any | None) -> dict[str, Any]:
    clips = []
    for number, title, subject in CLIPS:
        if client and not args.no_llm:
            try:
                clips.append(make_clip_with_llm(client, args.llm_model, number, title, subject))
                continue
            except Exception as error:
                print(f"LLM metadata failed for Clip {number}; using deterministic fallback: {error}")
        clips.append(build_clip(number, title, subject, fallback_scenes(subject), source="fallback"))
    return {
        "project": "ASMR Precision Cutting — Glass Fruit & Hard Gold",
        "createdAt": datetime.now(timezone.utc).isoformat(), "globalContinuity": GLOBAL_CONTINUITY,
        "delivery": {"clips": 10, "scenesPerClip": 32, "totalImages": 320, "status": "planned"}, "clips": clips,
    }


def generate_image(client: Any, prompt: str, image_model: str, size: str) -> bytes:
    response = client.images.generate(model=image_model, prompt=prompt, size=size, quality="medium", output_format="png")
    return base64.b64decode(response.data[0].b64_json)


def dashboard_html(project: dict[str, Any]) -> str:
    cards = []
    for clip in project["clips"]:
        thumbs = "".join(
            f'<button class="thumb" data-src="{clip["folder"]}/{s["imageFile"]}" data-label="{clip["clipId"]} · {s["sceneId"]}"><img loading="lazy" src="{clip["folder"]}/{s["imageFile"]}" alt="{s["sceneId"]}" onerror="this.parentElement.classList.add(\'missing\')"><span>{s["sceneId"]}</span></button>'
            for s in clip["scenes"]
        )
        cards.append(f'<section class="clip"><h2>{clip["clipId"].replace("_", " ")}</h2><p>{clip["subject"]}</p><div class="grid">{thumbs}</div></section>')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ASMR Production Dashboard</title><style>
*{{box-sizing:border-box}} body{{margin:0;background:#101114;color:#f2f2f2;font:14px system-ui,sans-serif}}header{{padding:32px max(24px,calc((100vw - 1280px)/2));background:linear-gradient(120deg,#191116,#281d0e)}}h1{{margin:0;font-size:28px}}header p{{color:#bdb8ac}}main{{max-width:1280px;margin:auto;padding:24px}}.clip{{border:1px solid #302f32;border-radius:12px;padding:18px;margin:18px 0;background:#18191d}}h2{{font-size:18px;margin:0}}.clip p{{color:#bbb;margin:6px 0 16px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(105px,1fr));gap:10px}}.thumb{{position:relative;aspect-ratio:16/10;border:1px solid #36363b;border-radius:7px;padding:0;overflow:hidden;background:#24252a;color:#fff;cursor:pointer}}.thumb img{{width:100%;height:100%;object-fit:cover;display:block}}.thumb span{{position:absolute;bottom:0;left:0;right:0;padding:3px 5px;text-align:left;background:#000a;font-size:11px}}.missing{{opacity:.45}}dialog{{max-width:min(92vw,1100px);padding:0;background:#111;color:white;border:1px solid #555;border-radius:12px}}dialog img{{display:block;max-width:90vw;max-height:75vh}}dialog p{{padding:0 14px}}dialog button{{margin:0 14px 14px}}@media(max-width:600px){{.grid{{grid-template-columns:repeat(4,1fr)}}}}
</style></head><body><header><h1>ASMR Production Dashboard</h1><p>10 clips · 320 scene images · click any frame to preview</p></header><main>{''.join(cards)}</main><dialog id="preview"><img id="full" alt=""><p id="label"></p><button onclick="preview.close()">Close</button></dialog><script>const preview=document.querySelector('#preview'),full=document.querySelector('#full'),label=document.querySelector('#label');document.querySelectorAll('.thumb').forEach(b=>b.onclick=()=>{{full.src=b.dataset.src;label.textContent=b.dataset.label;preview.showModal()}})</script></body></html>'''


def write_package(project: dict[str, Any], root: Path, client: Any | None, args: argparse.Namespace) -> None:
    root.mkdir(parents=True, exist_ok=True)
    images_created = 0
    for clip in project["clips"]:
        folder = root / clip["folder"]; folder.mkdir(exist_ok=True)
        for scene in clip["scenes"]:
            output = folder / scene["imageFile"]
            if output.exists() and args.skip_existing: continue
            if client and not args.metadata_only and (args.max_images == 0 or images_created < args.max_images):
                try:
                    output.write_bytes(generate_image(client, scene["imagePrompt"], args.image_model, args.image_size))
                    images_created += 1
                except Exception as error:
                    scene["imageError"] = str(error)
    actual = sum(1 for c in project["clips"] for s in c["scenes"] if (root / c["folder"] / s["imageFile"]).exists())
    project["delivery"].update({"imagesGenerated": actual, "status": f"[{actual}/320 PNG files generated]"})
    (root / "storyboard_index.json").write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "dashboard.html").write_text(dashboard_html(project), encoding="utf-8")
    archive = root.with_suffix(".zip")
    if archive.exists(): archive.unlink()
    shutil.make_archive(str(root), "zip", root.parent, root.name)
    print(f"Metadata: {root / 'storyboard_index.json'}\nDashboard: {root / 'dashboard.html'}\nZIP: {archive}\nImages: {actual}/320")


def main() -> None:
    parser = argparse.ArgumentParser(description="ASMR storyboard + image generation pipeline")
    parser.add_argument("--output", default="ASMR_Production_Output")
    parser.add_argument("--llm-model", default="gpt-5-mini")
    parser.add_argument("--image-model", default="gpt-image-1")
    parser.add_argument("--image-size", default="1536x1024")
    parser.add_argument("--max-images", type=int, default=0, help="0 means all 320; use 1 for a paid smoke test")
    parser.add_argument("--metadata-only", action="store_true", help="write JSON/dashboard/ZIP without generating PNGs")
    parser.add_argument("--no-llm", action="store_true", help="use the built-in deterministic S01–S32 storyboard")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()
    client = None
    if not args.metadata_only and not args.no_llm:
        if not os.getenv("OPENAI_API_KEY"):
            raise SystemExit("OPENAI_API_KEY is required unless --metadata-only or --no-llm is supplied.")
    if os.getenv("OPENAI_API_KEY") and not args.metadata_only:
        try:
            from openai import OpenAI
        except ImportError as error:
            raise SystemExit("Install dependencies first: python3 -m pip install -r requirements.txt") from error
        client = OpenAI()
    project = make_project(args, client)
    write_package(project, Path(args.output), client, args)


if __name__ == "__main__": main()
