#!/usr/bin/env bash
# ALWAYS ON - install the vendor binaries declared in
# config/build-update/vendor-binaries.yaml (OPS-17).
#
# WHY THIS EXISTS. Before it, the provisioner could rebuild the entire host and
# still could not put back a single AppImage: stage 40 printed "MANUAL fetch
# required" for each one and moved on. A vendor blob has no package source, so
# nothing else in the tree restores it. This is the script that closes that gap,
# and it closes it in the only defensible way - by REFUSING rather than by
# guessing.
#
# DESIGN RULES (README section 4.1):
#   * Digest-pinned. Every download is verified against a sha256 from the
#     manifest BEFORE it is put anywhere on disk. A mismatch is a hard stop and
#     the partial file is discarded, never moved into place.
#   * Dry run by default. Pass --yes to install.
#   * Never deletes. An existing file whose digest already matches is left
#     alone; one whose digest differs is reported and NOT overwritten (rules 2
#     and 3 - overwriting is an operator decision).
#   * Never writes a secret and never installs from an unpinned url.
#
# A note on the AppImage entries whose `url` is pinned to a version NEWER than
# the digest: QGroundControl is the live example. Its digest is 5.1.0 while its
# url is 5.1.5, so this script refuses it. That refusal is the feature. The
# alternative - verifying a 5.1.5 download against a 5.1.0 digest would fail, or
# dropping the check would install an unverified blob - is strictly worse.
set -Eeuo pipefail
IFS=$'\n\t'

AO_ROOT="${AO_ROOT:-/ALWAYSON}"
MANIFEST="${VENDOR_MANIFEST:-$AO_ROOT/config/build-update/vendor-binaries.yaml}"
CACHE="${AO_VENDOR_CACHE:-$AO_ROOT/cache/vendor}"
ASSUME_YES=0
[ "${1:-}" = "--yes" ] && ASSUME_YES=1

say()  { printf '%s\n' "$*"; }
log()  { printf '  %s\n' "$*"; }

[[ -f "$MANIFEST" ]] || { say "ERROR: manifest missing: $MANIFEST" >&2; exit 10; }
command -v python3 >/dev/null || { say "ERROR: python3 required" >&2; exit 10; }

mkdir -p "$CACHE"

# ---------------------------------------------------------------- plan
# Read the manifest and print what would happen, without fetching anything.
# python3 is used as the YAML reader because PyYAML is present for the other
# build-update scripts; if it is absent we say so rather than half-parsing.
read_manifest() {
  python3 - "$MANIFEST" <<'PY'
import json, sys
try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required to read %s" % sys.argv[1])
with open(sys.argv[1]) as fh:
    doc = yaml.safe_load(fh) or {}
rows = []
def s(v):
    """Digests and versions are strings in the schema, but YAML will happily
    coerce an all-numeric value to int - e.g. a sha256 written unquoted as
    0000...0 is parsed as the integer 0. Measured 2026-10-04: such an entry
    then printed as the EMPTY string via the `or ""` fallbacks below, so it
    silently degraded to 'no installed digest recorded' and reported OK - the
    one outcome a digest check must never produce.

    str() stops the degradation: the entry now reports DRIFT and the operator
    sees it. Note YAML has already dropped leading zeros by this point, so the
    compared value is `0`, not `0000...0`. That is why real digests in this
    manifest are QUOTED - a sha256 containing a-f is never coerced, and the
    quoted form is the one that round-trips exactly."""
    return None if v is None else str(v)

for e in doc.get("vendor_binaries") or []:
    rows.append({
        "id": s(e.get("id")), "name": s(e.get("name")),
        "path": s(e.get("path")), "install": s(e.get("install")) or "manual",
        "url": s(e.get("url")), "sha256": s(e.get("sha256")),
        "published": s(e.get("sha256_published_by_vendor")),
        "verifiable": bool(e.get("verifiable")),
        "installed_sha256": s(e.get("installed_sha256")),
        "version": s(e.get("version")), "drift": s(e.get("drift")),
        "member": s(e.get("member")),
    })
json.dump(rows, sys.stdout)
PY
}

entries="$(read_manifest)" || { say "ERROR: could not read manifest" >&2; exit 10; }
say "vendor binaries declared: $(printf '%s' "$entries" | python3 -c 'import json,sys;print(len(json.load(sys.stdin)))')"

installed=0; already=0; manual=0; refused=0; failed=0

# One entry at a time. `while read` over a here-string keeps the loop body in the
# current shell, which a pipe would not, and the counters must survive it.
while IFS= read -r e; do
  id="$(printf '%s' "$e"    | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"] or "")')"
  path="$(printf '%s' "$e" | python3 -c 'import json,sys;print(json.load(sys.stdin)["path"] or "")')"
  url="$(printf '%s' "$e"  | python3 -c 'import json,sys;print(json.load(sys.stdin)["url"] or "")')"
  sha="$(printf '%s' "$e"  | python3 -c 'import json,sys;print(json.load(sys.stdin)["sha256"] or "")')"
  pub="$(printf '%s' "$e"  | python3 -c 'import json,sys;print(json.load(sys.stdin)["published"] or "")')"
  kind="$(printf '%s' "$e" | python3 -c 'import json,sys;print(json.load(sys.stdin)["install"] or "manual")')"
  ver="$(printf '%s' "$e"  | python3 -c 'import json,sys;print(json.load(sys.stdin)["version"] or "-")')"
  ins="$(printf '%s' "$e"  | python3 -c 'import json,sys;print(json.load(sys.stdin)["installed_sha256"] or "")')"
  drift="$(printf '%s' "$e" | python3 -c 'import json,sys;print(json.load(sys.stdin)["drift"] or "-")')"
  member="$(printf '%s' "$e" | python3 -c 'import json,sys;print(json.load(sys.stdin)["member"] or "")')"
  [ -z "$id" ] && continue

  # --- already installed and verified -----------------------------------
  #
  # ORDER MATTERS, and the first revision got this wrong. The "no url" test
  # was checked FIRST and `continue`d, so an entry with no url was reported
  # MANUAL even when the file was sitting on disk with a matching digest.
  #
  # Measured 2026-10-04 on this host: lm-studio, pcloud and nperf were all
  # printed MANUAL, yet all three exist and all three hash to the manifest's
  # own recorded sha256:
  #   lm-studio   6e1c9e7973ae892eef93...  == manifest sha256  True
  #   pcloud      07e404be9e37ef2dffb6...  == manifest sha256  True
  #   nperf       13e422321043f1350384...  == manifest sha256  True
  #
  # That is the worst kind of report: it tells the operator a human must go
  # fetch files that are already installed and verified. "Cannot be fetched
  # automatically" and "is not installed" are different facts.
  #
  # So presence is checked FIRST. An entry with no url but a present, matching
  # file is reported OK (verified on disk, not auto-installable). An entry with
  # no url AND no file stays MANUAL, which is the genuine remaining gap.
  #
  # want = what a DOWNLOAD must hash to. want_disk = what the INSTALLED file
  # must hash to. Same value for an AppImage (the file IS the download);
  # different for an archive (download is .tar.gz, installed file is the
  # binary inside it). The first revision used one field for both and reported
  # a false DRIFT for every archive on a host where the binary was correct.
  want="${sha:-$pub}"
  if [ "$kind" = "appimage" ]; then
    want_disk="${ins:-$want}"
  else
    want_disk="$ins"
  fi

  # --- already installed: verify what is on disk -------------------------
  #
  # Checked BEFORE the "can we fetch it" question, on purpose (see above).
  if [ -f "$path" ]; then
    have="$(sha256sum "$path" | cut -d' ' -f1)"
    if [ -z "$want_disk" ]; then
      already=$((already + 1))
      say "OK      $id v$ver - present, no installed digest recorded to check against"
      log "path: $path"
      continue
    fi
    if [ "$have" = "$want_disk" ]; then
      already=$((already + 1))
      if [ -z "$url" ]; then
        say "OK      $id v$ver - present, digest matches (no url: not auto-installable)"
      else
        say "OK      $id v$ver - present, digest matches"
      fi
      continue
    fi
    say "DRIFT   $id v$ver at $path"
    log "on disk: $have"
    log "manifest installed_sha256: $want_disk"
    if [ -n "$pub" ] && [ "$have" = "$pub" ]; then
      log "on-disk file matches the VENDOR archive digest, which for an archive"
      log "entry is the wrong comparison - installed_sha256 is the field to fix."
    fi
    log "NOT overwritten (README 4.1 rules 2/3). Resolve by hand, or update the"
    log "manifest digest in one commit once the newer artifact is measured."
    refused=$((refused + 1))
    continue
  fi

  # --- not installed: can this host fetch it unattended? ----------------
  if [ "$kind" = "manual" ] || [ -z "$url" ]; then
    manual=$((manual + 1))
    say "MANUAL  $id (v$ver)"
    log "no url, or the vendor publishes no artifact; a human must place this file."
    log "expected at: $path"
    continue
  fi

  if [ -z "$want" ]; then
    refused=$((refused + 1))
    say "REFUSED $id - no digest to verify against. Not installing an unpinned download."
    continue
  fi

  if [ "$ASSUME_YES" -ne 1 ]; then
    say "[dry]   $id v$ver <- $url"
    log "verify $want, install to $path"
    continue
  fi

  # --- fetch ------------------------------------------------------------
  tmp="$CACHE/$(basename "$url")"
  say "FETCH   $id v$ver"
  if ! curl -fsSL --retry 3 --retry-delay 2 -o "$tmp.part" "$url"; then
    say "FAILED  $id - download failed"
    failed=$((failed + 1))
    continue
  fi
  got="$(sha256sum "$tmp.part" | cut -d' ' -f1)"
  if [ "$got" != "$want" ]; then
    # Do not leave a mismatched blob lying around to be "just reused" later.
    rm -f "$tmp.part"
    say "REFUSED $id - digest mismatch, nothing installed"
    log "expected $want"
    log "got      $got"
    if [ -n "$pub" ] && [ "$got" = "$pub" ]; then
      log "the download matches the vendor's digest for the PINNED url's version,"
      log "but the manifest's sha256 was measured from a DIFFERENT (older) file."
      log "Update the manifest sha256 to $pub only when upgrading deliberately."
    fi
    refused=$((refused + 1))
    continue
  fi
  mv "$tmp.part" "$tmp"

  # --- install ----------------------------------------------------------
  case "$kind" in
    appimage)
      install -d -m 0755 "$(dirname "$path")"
      install -m 0755 "$tmp" "$path"
      log "installed -> $path"
      ;;
    archive-extract)
      work="$(mktemp -d)"
      case "$tmp" in
        *.tar.gz|*.tgz) tar -xzf "$tmp" -C "$work" ;;
        *.zip)          unzip -q "$tmp" -d "$work" ;;
        *) say "FAILED  $id - unrecognised archive type"; failed=$((failed+1)); rm -rf "$work"; continue ;;
      esac
      src="$work/$member"
      if [ ! -f "$src" ]; then
        say "FAILED  $id - member '$member' not in archive"
        failed=$((failed + 1)); rm -rf "$work"; continue
      fi
      install -d -m 0755 "$(dirname "$path")"
      install -m 0755 "$src" "$path"
      log "installed -> $path"
      rm -rf "$work"
      ;;
    *)
      say "FAILED  $id - unknown install kind '$kind'"
      failed=$((failed + 1))
      continue
      ;;
  esac
  installed=$((installed + 1))
done <<<"$(printf '%s' "$entries" | python3 -c '
import json,sys
for r in json.load(sys.stdin):
    print(json.dumps(r))')"

say ""
say "installed=$installed  already-present=$already  manual=$manual  refused=$refused  failed=$failed"
if [ "$refused" -gt 0 ] || [ "$failed" -gt 0 ]; then
  say "Non-zero counts above are REPORTED findings, not a crash. Each is a"
  say "deliberate refusal or a real failure; see the lines above for which."
fi

# Exit contract. The first revision ended here unconditionally, so a DRIFT and
# a failed download were both reported with exit 0 - a provisioner whose
# failure signal is a line of text nobody is reading.
#
# `manual` is deliberately NOT a failure: it means "no vendor publishes an
# artifact", which is an operator phase of the rebuild (OPS-17), not a fault.
# Counting it would make every run of this script red.
#
# NOTE: provision.sh calls this through its `run` helper, which propagates the
# return code and is not guarded, so a non-zero here aborts stage 40.
if [ "$failed" -gt 0 ]; then
  say "exit 1: $failed download(s) or install(s) failed"
  exit 1
fi
if [ "$refused" -gt 0 ]; then
  say "exit 2: $refused entr(y/ies) refused - see DRIFT/REFUSED lines above"
  say "        Resolve by hand; nothing was overwritten (README 4.1 rules 2/3)."
  exit 2
fi
exit 0
[ "$failed" -eq 0 ]
