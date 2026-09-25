#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# sync-lmstudio-readme-preset.sh
#
# Regenerates the LM Studio config preset "ALWAYSON - FULL CONTEXT" so that
# every chat in LM Studio starts with the COMPLETE, current content of
# /ALWAYSON/README.md embedded in its system prompt, plus tuned sampling
# settings for accuracy on the Nemotron-3-Nano-4B model.
#
# Idempotent: exits without writing if the README hash is unchanged and the
# preset file already exists.
#
# Triggered by: systemd user path unit alwayson-lmstudio-preset-sync.path
#              (or run manually).
# ---------------------------------------------------------------------------
set -euo pipefail

README="${README:-/ALWAYSON/README.md}"
PRESET_DIR="${HOME}/.lmstudio/config-presets"
PRESET_FILE="${PRESET_DIR}/ALWAYSON - FULL CONTEXT.preset.json"
STATE_FILE="/ALWAYSON/logs/lmstudio-readme-preset.sha256"

[ -f "$README" ] || { echo "ERROR: $README not found" >&2; exit 1; }
mkdir -p "$PRESET_DIR" "$(dirname "$STATE_FILE")"

NEW_HASH="$(sha256sum "$README" | cut -d' ' -f1)"
OLD_HASH=""
[ -f "$STATE_FILE" ] && OLD_HASH="$(cat "$STATE_FILE")"

if [ "$NEW_HASH" = "$OLD_HASH" ] && [ -f "$PRESET_FILE" ]; then
    # Verify the preset is still valid JSON before trusting it.
    if python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$PRESET_FILE" 2>/dev/null; then
        exit 0
    fi
fi

export README PRESET_FILE NEW_HASH
python3 - <<'PYEOF'
import json, os, datetime

readme_path = os.environ["README"]
preset_path = os.environ["PRESET_FILE"]
new_hash = os.environ["NEW_HASH"]

with open(readme_path, "r", encoding="utf-8") as f:
    content = f.read()

stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

system_prompt = f"""ALWAYS ON - PROJECT KNOWLEDGE (authoritative document embedded below)

You are the ALWAYS ON project assistant. The complete, verbatim content of
/ALWAYSON/README.md is included below between the BEGIN/END markers. It is
your single source of truth for every question about the ALWAYS ON project.

RULES:
1. Base every answer on the document below. When it supports your answer,
   cite the section by its exact heading title (for example "Section 4.4
   Approved Internal Paths" - quote the heading text as written in the
   document). Do not guess numeric section labels; quote the heading so the
   citation can be verified by text search.
2. If the document does not cover something, say so explicitly. Never invent
   architecture, ports, credentials, addresses, or status.
3. The document defines categories - Architecture requirement, Implemented,
   Planned, Blocked, Deviation, Work item, Issue. Preserve those distinctions
   when reporting status.
4. Be concise, concrete, and complete. When the user asks for work that
   touches the project, check the relevant sections first.

DOCUMENT SNAPSHOT: updated {stamp} (sha256 {new_hash[:16]})

===== BEGIN /ALWAYSON/README.md =====
{content}
===== END /ALWAYSON/README.md ====="""

preset = {
    "identifier": "@local:alwayson-full-context",
    "name": "ALWAYSON - FULL CONTEXT",
    "changed": True,
    "operation": {
        "fields": [
            {"key": "llm.prediction.systemPrompt", "value": system_prompt},
            # Reasoning model: more thinking = better accuracy (was 1024).
            {"key": "llm.prediction.reasoning.budgetTokens",
             "value": {"checked": True, "value": 4096}},
            # Accuracy-oriented sampling for a small model.
            {"key": "llm.prediction.temperature", "value": 0.3},
            {"key": "llm.prediction.topPSampling",
             "value": {"checked": True, "value": 0.95}},
            {"key": "llm.prediction.minPSampling",
             "value": {"checked": True, "value": 0.05}},
            {"key": "llm.prediction.repeatPenalty",
             "value": {"checked": True, "value": 1.05}},
        ]
    },
    "load": {
        "fields": [
            {"key": "llm.load.llama.autoFit", "value": True},
            {"key": "llm.load.llama.keepModelInMemory", "value": True},
        ]
    },
}

tmp_path = preset_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8") as f:
    json.dump(preset, f, indent=2, ensure_ascii=False)
    f.write("\n")
os.replace(tmp_path, preset_path)  # atomic

print(f"WROTE {preset_path} ({os.path.getsize(preset_path)} bytes, "
      f"readme sha256 {new_hash[:16]})")
PYEOF

# Only mark as synced after the preset exists and parses.
python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$PRESET_FILE"
printf '%s\n' "$NEW_HASH" > "$STATE_FILE.tmp"
mv "$STATE_FILE.tmp" "$STATE_FILE"
echo "OK: preset synchronized with $README (sha256 ${NEW_HASH:0:16})"
