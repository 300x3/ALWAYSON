# ALWAYS ON - detect-heltec.sh: locate Heltec V3 on a stable /dev/serial/by-id path.
set -Eeuo pipefail
IFS=$'\n\t'
if [[ ! -d /dev/serial/by-id ]]; then
  echo "PENDING: no serial devices present - connect the Heltec WiFi LoRa 32 V3 via USB-C"
  exit 3
fi
matches="$(ls /dev/serial/by-id/ | grep -i 'heltec\|esp32\|sx1262\|cp2102\|cp210x\|silicon_labs' || true)"
[[ -n "$matches" ]] && { echo "OK:"; echo "$matches"; exit 0; }
echo "PENDING: serial devices exist but none matched Heltec/ESP32/SX1262:"
ls /dev/serial/by-id/
exit 4
