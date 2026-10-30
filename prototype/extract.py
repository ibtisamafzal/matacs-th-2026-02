"""Optional: run the extraction prompt on proposal text files.

Put proposal text files in prototype/proposals/ (git-ignored; do not commit them).
Needs ANTHROPIC_API_KEY in your environment or a .env file (see .env.example).
Usage: python extract.py
"""
import json
import os
import re
from datetime import date
from pathlib import Path

import anthropic

MODEL = os.environ.get("MODEL_NAME", "claude-sonnet-4-5")
ROOT = Path(__file__).parent


def load_prompt_parts():
    """Pull the system and user templates out of ../PROMPTS.md."""
    text = (ROOT.parent / "PROMPTS.md").read_text()
    system = re.search(r"SYSTEM:\n(.*?)\n\nUSER:", text, re.S).group(1)
    user = re.search(r"USER:\n(.*?)\n\n# Reason prompt", text, re.S).group(1)
    return system, user


def main():
    system, user_tpl = load_prompt_parts()
    criteria = (ROOT / "criteria.json").read_text()
    client = anthropic.Anthropic()
    out = {}
    for path in sorted((ROOT / "proposals").glob("*.txt")):
        user = (user_tpl.replace("{{criteria_json}}", criteria)
                        .replace("{{date}}", date.today().isoformat())
                        .replace("{{proposal_text}}", path.read_text()))
        msg = client.messages.create(model=MODEL, max_tokens=1500, temperature=0,
                                     system=system,
                                     messages=[{"role": "user", "content": user}])
        raw = msg.content[0].text
        out[path.stem] = json.loads(raw)
        # Quote check: every evidence quote must appear in the source text.
        source = path.read_text()
        for key, val in out[path.stem].items():
            ev = val.get("evidence") if isinstance(val, dict) else None
            if ev and ev not in source:
                val["confidence"] = "low"
                val["quote_check"] = "FAILED"
    (ROOT / "extracted.json").write_text(json.dumps(out, indent=1))
    print("Wrote extracted.json for", len(out), "proposals")


if __name__ == "__main__":
    main()
