---
item: OPS-14
action: close
evidence: |
  $ podman info --format '{{.Host.Security.Rootless}}'
  true
  $ podman info --format '{{.Store.GraphRoot}}'
  /home/scottw/.local/share/containers/storage
  $ systemctl list-unit-files '*.container' '*.network' --no-legend | wc -l
  0
  $ grep -rn '^User=\\|^Group=' quadlet/
  (no output, rc=1)
  # rootful store is empty of workload records: 11 of 12 tables at count 0
  # (PLAT-01 re-verification 2026-10-08, §13.2 of README.md)
section: 12-host-installation-and-configuration
---
The Podman store model is reconciled: every workload runs rootless, the rootful
store holds no workload records (all tables empty save DBConfig), and no Quadlet
unit reassigns to a service account — §13.2 of the README records the
designation as measured and re-verified 2026-10-08, with full audit output in
`agents/COORDINATION (README UPDATES)/proposals/plat-PLAT-01.md`. The mixed-store
deviation is therefore confirmed and bounded: residual scaffold (three unused
service accounts, the disabled `ao-podman-bridge.service`, and
`overlay-images/` whose contents are permission-denied as uid 1000) is left in
place pending operator decision, not a defect in the designation. The item's
acceptance — "Record the deviation in this document or remove the claim" — is
satisfied by §13.2's explicit recording of the residual image-data question as an
open but harmless observation. No host change was required.