#!/bin/bash
# ao-merge-5pm: one-shot merge batch scheduled by the operator for 2026-10-11 17:00 PDT.
# Merges the 11 ai-<group> session branches into main one at a time (restart doc §8),
# checks the compile gate after each, runs the proposals compiler, re-renders the
# dashboard, and posts a note. Does NOT commit or push (operator-gated per standing rule).
# Triggered by ao-merge-5pm.timer (one-shot, today only).
set -u
cd /ALWAYSON || exit 1
LOG=/tmp/ao-merge-5pm.log
{
echo "=== merge batch started $(date -u '+%F %H:%M UTC') ==="
for g in plat net sec ledger pay comm field sim ops-a ops-b spec; do
  echo "--- merging ai-$g ---"
  git merge --no-edit "ai-$g" 2>&1 | tail -2
  python3 "agents/COORDINATION (README UPDATES)/tools/compile.py" --check 2>&1 | tail -1
done
echo "--- proposals compiler ---"
python3 scripts/orchestration/compile-proposals.py 2>&1 | tail -5
echo "--- dashboard ---"
bash scripts/orchestration/dashboard.sh 2>&1 | tail -2
python3 scripts/orchestration/dashboard-note.py --who coordinator --level done \
  "17:00 merge batch done: session branches merged, proposals compiled -- review git status before commit/push" 2>&1 | tail -1
echo "=== merge batch finished $(date -u '+%F %H:%M UTC') ==="
} >> "$LOG" 2>&1
