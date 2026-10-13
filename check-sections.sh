#!/usr/bin/env bash
# Inspect status/re-vision markers in ALWAYSON section sources
cd /ALWAYSON || exit 1
grep -rnE 'Re-verification|Correction [0-9-]|Alternative|Decision|Caveat|no status, history' 'agents/COORDINATION (README UPDATES)/' --include='section.md' | head -80
