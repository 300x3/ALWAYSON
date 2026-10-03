#!/usr/bin/env python3
"""strip-collada-lines — remove Collada <lines> blocks from a .dae mesh.

ALWAYS ON fabrication simulation support tool (README §10.2.1).

WHY THIS EXISTS
  The four SketchUp exports in /ALWAYSON/GAZEBO carry SketchUp edge geometry as
  Collada <lines> elements. gz-common's ColladaLoader builds a std::string from
  a NULL attribute in that element and throws:

      terminate called after throwing an instance of 'std::logic_error'
        what():  basic_string: construction from null is not valid

  Because that throw happens inside a Qt event handler, the Gazebo Sim 10 GUI
  client cannot catch it: the process aborts roughly one second after
  "Camera pose topic advertised", on the first rendered frame.

  SCOPE CORRECTION (2026-10-01): this docstring records the fault as a
  COLLISION-path problem only. That is where it was first hit, headless
  `gz sim -s` loading collision geometry. It is NOT collision-specific. The
  Gazebo Sim 10 GUI also aborts on the VISUAL path, via:

      gz::sim::v10::RenderUtil::Update()
        -> SceneManager::CreateVisual()
        -> SceneManager::LoadGeometry()
        -> gz::sim::v10::loadMesh()
        -> gz::common::MeshManager::Load()
        -> gz::common::ColladaLoader::Load()
        -> ColladaLoader::Implementation::LoadGeometry()   <-- throws

  A primitive collision proxy cannot fix that, because the crash is in the
  visual mesh. The visual assets are sanitised by
  scripts/simulation/strip-collada-lines.py, which removes the offending
  <lines> elements. See
  logs/operations/gazebo-gui-visual-mesh-and-monitor-placement-2026-10-01.log.

  Skinned-mesh work is unaffected: only the <lines> elements are removed.
  <triangles>, <polylist>, <vertices>, <accessor> and <float_array> payloads are
  copied through byte-for-byte, so rendered geometry is unchanged.

SAFETY
  Never edits a source export in place. Writes to an output directory and
  reports what it did, so the original SketchUp exports are preserved.

USAGE
  strip-collada-lines.py SRC.dae OUT.dae [SRC.dae OUT.dae ...]
  strip-collada-lines.py --in-place FILE.dae      # refuses; see SAFETY
"""

import re
import sys
import pathlib

# Paired form: <lines> ... </lines>. SketchUp emits these in bulk, one per edge
# group, and they are frequently multi-line, so DOTALL is required.
LINES_PAIRED = re.compile(rb"<lines\b.*?</lines\s*>", re.DOTALL)
# Self-closing/empty form: <lines id="..." count="0"/> or bare <lines/>.
LINES_EMPTY = re.compile(rb"<lines\b[^>]*/>")


def strip_lines(data: bytes) -> tuple[bytes, int, int]:
    """Return (stripped_bytes, blocks_removed, bytes_removed)."""
    before = len(data)
    out, n_paired = LINES_PAIRED.subn(b"", data)
    out, n_empty = LINES_EMPTY.subn(b"", out)
    removed = n_paired + n_empty
    return out, removed, before - len(out)


def main(argv):
    if len(argv) < 3 or len(argv) % 2 != 1:
        sys.stderr.write(__doc__)
        return 2

    failures = 0
    for i in range(1, len(argv), 2):
        src, dst = pathlib.Path(argv[i]), pathlib.Path(argv[i + 1])
        if not src.is_file():
            print(f"ERROR {src}: not a file", file=sys.stderr)
            failures += 1
            continue

        data = src.read_bytes()
        out, removed, delta = strip_lines(data)

        # Guard against a regex that silently ate the whole document.
        if removed and b"<triangles" not in out:
            print(f"ERROR {src}: no <triangles> survived; refusing to write",
                  file=sys.stderr)
            failures += 1
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(out)
        print(f"{src.name}: removed {removed} <lines> block(s), "
              f"-{delta} bytes -> {dst}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
