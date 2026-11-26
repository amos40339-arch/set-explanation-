"""
Generate the Nigerian-voice narration for Sets Made Simple.

Setup (once):
    pip install edge-tts

Hear both Nigerian voices first and pick one:
    python gen_voice.py --sample

Generate all clips (default voice: Abeo, male):
    python gen_voice.py
    python gen_voice.py --voice en-NG-EzinneNeural     # female voice instead

Clips are saved to ./audio/<clip id>.mp3, next to index.html.
Re-running skips clips that already exist, so if your network drops, just run it again.
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts is not installed. Run:  pip install edge-tts")

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "narration-script.txt"
OUT = HERE / "audio"
ID_LINE = re.compile(r"^L\d+-S\d{2}-B\d+$")

VOICES = {
    "en-NG-AbeoNeural": "Abeo (male, Nigerian English)",
    "en-NG-EzinneNeural": "Ezinne (female, Nigerian English)",
}


def load_clips(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    clips = []
    for i, line in enumerate(lines):
        if ID_LINE.match(line.strip()) and i + 1 < len(lines):
            text = lines[i + 1].strip()
            if text:
                clips.append((line.strip(), text))
    return clips


async def make_clip(clip_id, text, voice, rate, pitch, sem, retries=3):
    target = OUT / f"{clip_id}.mp3"
    if target.exists() and target.stat().st_size > 1000:
        return "skipped"
    async with sem:
        for attempt in range(1, retries + 1):
            try:
                tmp = target.with_suffix(".part")
                await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(str(tmp))
                tmp.replace(target)
                return "made"
            except Exception as exc:  # network hiccups are common; retry
                if attempt == retries:
                    print(f"  FAILED {clip_id}: {exc}")
                    return "failed"
                await asyncio.sleep(2 * attempt)


async def run_all(voice, rate, pitch):
    if not SCRIPT.exists():
        sys.exit(f"Can't find {SCRIPT.name}. Keep it in the same folder as this script.")
    clips = load_clips(SCRIPT)
    OUT.mkdir(exist_ok=True)
    print(f"Voice: {VOICES.get(voice, voice)}  |  {len(clips)} clips  |  rate {rate}  |  pitch {pitch}")
    sem = asyncio.Semaphore(4)
    results = {"made": 0, "skipped": 0, "failed": 0}
    tasks = [make_clip(cid, text, voice, rate, pitch, sem) for cid, text in clips]
    for n, coro in enumerate(asyncio.as_completed(tasks), 1):
        results[await coro] += 1
        print(f"\r  {n}/{len(clips)} done", end="", flush=True)
    print()
    print(f"Made {results['made']}, skipped {results['skipped']} (already there), failed {results['failed']}.")
    if results["failed"]:
        print("Some clips failed. Run the same command again to retry only those.")
    else:
        print("All done. Publish this whole folder (index.html + audio).")


async def run_sample(rate):
    OUT.mkdir(exist_ok=True)
    line = "Good day, class. Today we're learning sets, and I promise you, it's easier than it looks."
    for voice, label in VOICES.items():
        out = HERE / f"sample-{voice}.mp3"
        await edge_tts.Communicate(line, voice, rate=rate).save(str(out))
        print(f"Saved {out.name}  ->  {label}")
    print("Play both, pick one, then run:  python gen_voice.py --voice <voice name>")


def main():
    ap = argparse.ArgumentParser(description="Generate Nigerian-voice narration clips.")
    ap.add_argument("--voice", default="en-NG-AbeoNeural", help="en-NG-AbeoNeural or en-NG-EzinneNeural")
    ap.add_argument("--rate", default="+0%", help="speed, e.g. -10%% slower, +0%% normal")
    ap.add_argument("--pitch", default="-3Hz", help="voice pitch, e.g. -3Hz deeper, +0Hz normal")
    ap.add_argument("--sample", action="store_true", help="make one sample of each Nigerian voice")
    args = ap.parse_args()
    if args.sample:
        asyncio.run(run_sample(args.rate))
    else:
        asyncio.run(run_all(args.voice, args.rate, args.pitch))


if __name__ == "__main__":
    main()
