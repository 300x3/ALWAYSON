#!/bin/sh
# ALWAYS ON work dashboard - regenerate the HTML and refresh hourly snapshots.
cd /ALWAYSON || exit 1
python3 scripts/orchestration/collect-metrics.py >/dev/null 2>&1
python3 scripts/orchestration/render-dashboard.py >/dev/null 2>&1
echo "dashboard refreshed $(date -u +%H:%MZ)"
