#!/usr/bin/env python3
"""compute-mesh-aabb — axis-aligned bounds of a Collada (.dae) mesh.

ALWAYS ON fabrication simulation support tool (README §10.2.1 "3D world
setup"; the same bounds feed the §10.2.1 boning/datum frames later).

WHY THIS EXISTS
  The four SketchUp exports in /ALWAYSON/GAZEBO carry SketchUp edge geometry as
  Collada <lines> elements. gz-common's ColladaLoader aborts on that element
  when the mesh is loaded as a COLLISION shape:
      terminate called after throwing an instance of 'std::logic_error'
        what():  basic_string: construction from null is not valid
  (ColladaLoader::Implementation::LoadLines). Headless `gz sim -s` loads only
  collision geometry, so a mesh collision aborts the server. The fix is a
  deterministic primitive collision proxy sized from the real mesh bounds,
  which this tool computes.

WHAT IT DOES
  Walks the Collada visual scene, accumulating <node><matrix> transforms
  (Collada matrices are column-major, 16 floats), and transforms every
  POSITION float_array reachable through <instance_geometry>. Reports the
  union min/max, size, and centre in the file's own units and in metres.

UNITS
  These exports declare <unit meter="0.0254" name="inch"/> and do NOT bake the
  conversion into their matrices, so raw coordinates are inches. Metres are
  therefore inches * 0.0254, which is exactly what the SDF
  <scale>0.0254</scale> applies to the rendered mesh. Collision box size and
  pose must use the metre values.

USAGE
  python3 compute-mesh-aabb.py FILE.dae [FILE.dae ...]
  python3 compute-mesh-aabb.py --sdf FILE.dae      # emit SDF box snippets
  python3 compute-mesh-aabb.py --column-major ...  # strict-spec reading
"""

import sys
import xml.etree.ElementTree as ET

INCH_M = 0.0254

# MATRIX CONVENTION — verified against gz-common source, not assumed.
#   gz-common ColladaLoader::LoadNodeTransform does:
#       transform.Set(values[0], values[1], ... values[15]);
#   and gz-math Matrix4::Set maps its first four arguments to ROW 0
#   (data[0][0..3]), so values[3] becomes data[0][3] — the translation X.
#   gz-common therefore reads a Collada <matrix> as ROW-major, which is how
#   these SketchUp exports store it (row 3 is always "0 0 0 1" and the
#   translation sits at indices 3/7/11). Under a strict column-major reading
#   the same files yield zero translation and flattened results, which does
#   not match what gz renders.
#   Default = row-major, i.e. reproduce exactly what gz-common does.
#   --column-major is available for cross-checking against a strict
#   Collada-spec reader.
TRANSPOSE = True


def local(tag):
    return tag.rsplit('}', 1)[-1]


def parse_matrix(text):
    v = [float(x) for x in text.split()]
    if len(v) != 16:
        raise ValueError('matrix must have 16 floats, got %d' % len(v))
    if TRANSPOSE:
        # row-major storage index r*4+c -> column-major index c*4+r, so the
        # column-major transform_point()/mat_mul() helpers below see gz's
        # reading of the same file.
        return [v[row * 4 + col] for col in range(4) for row in range(4)]
    return v


def identity():
    return [1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0]


def mat_mul(a, b):
    """Column-major 4x4 multiply: returns a*b."""
    out = [0.0] * 16
    for col in range(4):
        for row in range(4):
            out[col * 4 + row] = sum(
                a[k * 4 + row] * b[col * 4 + k] for k in range(4))
    return out


def transform_point(m, x, y, z):
    return (
        m[0] * x + m[4] * y + m[8] * z + m[12],
        m[1] * x + m[5] * y + m[9] * z + m[13],
        m[2] * x + m[6] * y + m[10] * z + m[14],
    )


def parse_float_array(elem):
    text = elem.text or ''
    try:
        return [float(t) for t in text.split()]
    except ValueError:
        return []


def geometry_positions(geom):
    """Return a list of (x, y, z) tuples for a <geometry> POSITION source.

    Uses the <vertices> POSITION input to pick the right source; falls back to
    every float_array in the geometry when no <vertices> link resolves.
    """
    mesh = None
    for child in geom:
        if local(child.tag) == 'mesh':
            mesh = child
            break
    if mesh is None:
        return []

    sources = {}
    arrays = {}
    for child in mesh:
        tag = local(child.tag)
        if tag == 'source':
            sid = child.get('id') or child.get('name')
            for sub in child:
                if local(sub.tag) == 'float_array' and sid:
                    sources[sid] = parse_float_array(sub)
        elif tag == 'float_array':
            arrays[child.get('id')] = parse_float_array(child)

    pos_source_ids = []
    for child in mesh:
        if local(child.tag) == 'vertices':
            for sub in child:
                if local(sub.tag) == 'input' and sub.get('semantic') == 'POSITION':
                    ref = (sub.get('source') or '').lstrip('#')
                    if ref:
                        pos_source_ids.append(ref)

    vals = None
    for ref in pos_source_ids:
        if sources.get(ref):
            vals = sources[ref]
            break
    if vals is None:
        for ref in pos_source_ids:
            if arrays.get(ref):
                vals = arrays[ref]
                break
    if vals is None:
        merged = []
        for v in sources.values():
            merged.extend(v)
        vals = merged

    if not vals or len(vals) % 3:
        return []
    return list(zip(vals[0::3], vals[1::3], vals[2::3]))


def compute(path):
    """Return the union transformed AABB of every instanced geometry."""
    root = ET.parse(path).getroot()

    geoms = {}
    for elem in root.iter():
        if local(elem.tag) == 'geometry':
            gid = elem.get('id')
            if gid:
                geoms[gid] = elem

    lo = [float('inf')] * 3
    hi = [float('-inf')] * 3
    counter = {'n': 0}
    unresolved = []

    def walk(node, parent):
        # Collada composes a node's transform in document order, so the
        # accumulator must persist across siblings (matrix, then
        # instance_geometry) rather than reset per child.
        m = parent
        for child in node:
            tag = local(child.tag)
            if tag == 'node':
                walk(child, m)
            elif tag == 'matrix':
                m = mat_mul(m, parse_matrix(child.text or ''))
            elif tag == 'translate':
                v = [float(x) for x in (child.text or '').split()]
                if len(v) == 3:
                    t = identity()
                    t[12], t[13], t[14] = v
                    m = mat_mul(m, t)
            elif tag == 'scale':
                v = [float(x) for x in (child.text or '').split()]
                if len(v) == 3:
                    s = identity()
                    s[0], s[5], s[10] = v
                    m = mat_mul(m, s)
            elif tag == 'instance_geometry':
                ref = (child.get('url') or '').lstrip('#')
                geom = geoms.get(ref)
                if geom is None:
                    unresolved.append(ref)
                    continue
                for (x, y, z) in geometry_positions(geom):
                    px, py, pz = transform_point(m, x, y, z)
                    counter['n'] += 1
                    for i, val in enumerate((px, py, pz)):
                        if val < lo[i]:
                            lo[i] = val
                        if val > hi[i]:
                            hi[i] = val
            # <rotate> / <lookat> / <skew> are not emitted by these SketchUp
            # exports (they use <matrix>); ignored deliberately rather than
            # mis-applied.

    for elem in root.iter():
        if local(elem.tag) == 'visual_scene':
            walk(elem, identity())

    if counter['n'] == 0:
        return None
    return {'path': path, 'vertices': counter['n'], 'lo': lo, 'hi': hi,
            'unresolved': unresolved}


def report(r, sdf=False):
    lo, hi = r['lo'], r['hi']
    size = [hi[i] - lo[i] for i in range(3)]
    ctr = [(hi[i] + lo[i]) / 2.0 for i in range(3)]
    size_m = [s * INCH_M for s in size]
    ctr_m = [c * INCH_M for c in ctr]
    print(r['path'])
    print('  transformed POSITION vertices : %d' % r['vertices'])
    if r['unresolved']:
        print('  WARNING unresolved geometry refs: %s'
              % sorted(set(r['unresolved']))[:5])
    print('  inches  min %8.2f %8.2f %8.2f   max %8.2f %8.2f %8.2f'
          % (lo[0], lo[1], lo[2], hi[0], hi[1], hi[2]))
    print('  metres  size %.4f %.4f %.4f   centre %.4f %.4f %.4f'
          % (size_m[0], size_m[1], size_m[2], ctr_m[0], ctr_m[1], ctr_m[2]))
    if sdf:
        print('        <collision name="collision">')
        print('          <pose>%.6f %.6f %.6f 0 0 0</pose>'
              % (ctr_m[0], ctr_m[1], ctr_m[2]))
        print('          <geometry>')
        print('            <box><size>%.6f %.6f %.6f</size></box>'
              % (size_m[0], size_m[1], size_m[2]))
        print('          </geometry>')
        print('        </collision>')


def main(argv):
    global TRANSPOSE
    args = [a for a in argv[1:] if not a.startswith('--')]
    sdf = '--sdf' in argv
    TRANSPOSE = '--column-major' not in argv
    if not args:
        print(__doc__.strip())
        return 2
    rc = 0
    for path in args:
        try:
            r = compute(path)
        except (ET.ParseError, OSError, ValueError) as exc:
            print('%s: ERROR %s' % (path, exc))
            rc = 1
            continue
        if r is None:
            print('%s: no geometry positions found' % path)
            rc = 1
            continue
        report(r, sdf=sdf)
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv))
