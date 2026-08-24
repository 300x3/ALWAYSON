# ALWAYS ON - report-disk-usage.sh
set -Eeuo pipefail
IFS=$'\n\t'
df -hT / /media/scottw/500GBPHOTOGRAM
du -sh /ALWAYSON/data/* /ALWAYSON/backups/* /ALWAYSON/artifacts/* 2>/dev/null || true
