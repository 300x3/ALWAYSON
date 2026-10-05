#!/usr/bin/env bash
# ALWAYS ON - validation: check-image-digests.sh
#
# OPS-02. The version matrix records image digests as free text, so the only
# way a row changes is a hand edit and a stale row is indistinguishable from a
# correct one by reading it. This compares every digest in
# config/platform/version-matrix.yaml against the digests the DEPLOYED units
# actually carry, and reports the differences.
#
# The deployed units are the authority -- not the matrix, and not the repository
# quadlet/ tree. Quadlet deploys FLAT: ~/.config/containers/systemd/ holds
# copies, not symlinks, so the repository copy can be correct while the live
# unit runs something else. Comparing against the repo would report "no drift"
# at exactly the moment the live system had drifted.
#
# It also verifies a property capture-version-matrix.sh cannot: that every
# deployed Image= is digest-pinned at all. A tag-only Image= passes review for
# months and is a README 4.1 rule 9 violation the whole time.
#
# Read-only. It reports; it never rewrites the matrix. Where a row disagrees
# with the live system, deciding which side is right is an operator call, not a
# script's -- silently adopting the live digest would launder a hand edit into
# an apparently-captured fact. `--check` exits 1 so a timer or CI can gate on it.
set -Eeuo pipefail
IFS=$'\n\t'
. "${AO_ROOT:-/ALWAYSON}/scripts/lib/common.sh"

# Both paths are overridable so the checker can be exercised against a synthetic
# tree in a test. A check whose OK path has never been observed is a check whose
# DRIFT result proves nothing.
UNIT_DIR="${QUADLET_DEPLOY_DIR:-$HOME/.config/containers/systemd}"
MATRIX="${VERSION_MATRIX:-$AO_ROOT/config/platform/version-matrix.yaml}"

check_only=0
[[ "${1:-}" == "--check" ]] && check_only=1

[[ -f "$MATRIX" ]] || { echo "ERROR: $MATRIX missing" >&2; exit 10; }
[[ -d "$UNIT_DIR" ]] || { echo "ERROR: no deployed units at $UNIT_DIR" >&2; exit 10; }

# Every digest the live system is actually running.
#
# `|| true` is load-bearing. When every deployed image is unpinned, this grep
# matches nothing and exits 1; under `set -e` + `pipefail` that aborted the
# script with status 1 and NO output -- a gate that fails without saying why.
# The unpinned images are the most important thing it can report, so it must
# reach the reporting code rather than die in the collection code.
deployed="$(
  { grep -h '^Image=' "$UNIT_DIR"/*.container 2>/dev/null || true; } \
    | { grep -oE 'sha256:[0-9a-f]{64}' || true; } \
    | sort -u
)"

n_units="$(find "$UNIT_DIR" -maxdepth 1 -name '*.container' | wc -l)"
n_dep="$(grep -c . <<<"$deployed" || true)"
echo "deployed units  : $n_units in $UNIT_DIR"
echo "distinct digests: $n_dep"

# Rule 9: an Image= with no digest is a live violation whatever the matrix says.
unpinned=0
while IFS= read -r line; do
  [[ -n "$line" ]] || continue
  if ! grep -qE '@sha256:[0-9a-f]{64}' <<<"$line"; then
    unpinned=$((unpinned + 1))
    printf 'UNPINNED  %s\n' "$line"
  fi
done < <(grep -h '^Image=' "$UNIT_DIR"/*.container 2>/dev/null | sort -u)

# Every digest the matrix claims, keyed by the yaml path it was found under.
matrix_digests="$(
  python3 - "$MATRIX" <<'PY'
import re, sys, yaml
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")

def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}{k}.")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}{i}.")
    elif isinstance(node, str):
        for d in DIGEST.findall(node):
            yield path[:-1], d

for path, d in walk(yaml.safe_load(open(sys.argv[1]))):
    print(f"{path}\t{d}")
PY
)"

drift=0
matched=0
while IFS=$'\t' read -r path digest; do
  [[ -n "${digest:-}" ]] || continue
  if grep -qxF "$digest" <<<"$deployed"; then
    matched=$((matched + 1))
  else
    drift=$((drift + 1))
    printf 'DRIFT     %-40s %s\n' "$path" "$digest"
  fi
done <<<"$matrix_digests"

echo
echo "matrix digests matched a deployed unit  : $matched"
echo "matrix digests matching nothing deployed: $drift"
echo "deployed Image= lines without a digest  : $unpinned"

# The converse: deployed but unlisted. Not drift -- the matrix need not name
# every image -- but a local build or a tag-only image is worth seeing.
while IFS= read -r d; do
  [[ -n "$d" ]] || continue
  if ! cut -f2 <<<"$matrix_digests" | grep -qxF "$d"; then
    printf 'UNLISTED  deployed but absent from the matrix: %s\n' "$d"
  fi
done <<<"$deployed"

if (( drift > 0 || unpinned > 0 )); then
  echo
  echo "RESULT: DRIFT -- $drift stale matrix row(s), $unpinned unpinned deployed image(s)."
  echo "Resolve each by hand: the matrix row and the live unit cannot both be right."
  (( check_only )) && exit 1
  exit 0
fi

echo
echo "RESULT: OK -- every matrix digest is carried by a deployed unit, and every deployed image is pinned."
exit 0