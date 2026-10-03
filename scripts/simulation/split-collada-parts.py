#!/usr/bin/env python3
"""split-collada-parts — split a monolithic Collada .dae into per-part .dae files.

WHY
  The ALWAYS ON factory SketchUp exports are single monolithic meshes
  (arms 336, conveyor 220, massing 106 sub-meshes) under anonymous
  group_N nodes. Nothing can articulate until each moving part is its own
  mesh file with its own SDF link and joint. This tool performs that split.

IDENTIFICATION
  Parts are selected by their WORLD-SPACE AABB signature, in the source
  file's own units (inches; the world applies scale 0.0254 at link level).
  Signature = (dx, dy, dz) rounded to whole inches. SketchUp's own
  geometry is regular enough that e.g. the 36"x80" doors appear as a single
  repeated size class.

USAGE
  split-collada-parts.py SRC.dae --list
  split-collada-parts.py SRC.dae --size DX,DY,DZ --out OUTDIR --prefix NAME

Transforms are baked into vertex positions, so emitted parts are already in
world space and need no node hierarchy. Triangles only; normals are dropped
(gz-rendering computes them).
"""
import argparse, pathlib, sys
import xml.etree.ElementTree as ET

NS = '{http://www.collada.org/2005/11/COLLADASchema}'


def ident():
    return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)]
            for i in range(4)]


def node_matrix(node):
    import math
    m = ident()
    for el in node:
        t = el.tag
        if t == NS + 'matrix':
            v = [float(x) for x in el.text.split()]
            # Collada composes <matrix> BEFORE the parent frame, so PRE-multiply.
            m = mul([[v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]],
                     [v[8], v[9], v[10], v[11]], [v[12], v[13], v[14], v[15]]], m)
        elif t == NS + 'translate':
            v = [float(x) for x in el.text.split()]
            m = mul(m, [[1, 0, 0, v[0]], [0, 1, 0, v[1]], [0, 0, 1, v[2]], [0, 0, 0, 1]])
        elif t == NS + 'scale':
            v = [float(x) for x in el.text.split()]
            m = mul(m, [[v[0], 0, 0, 0], [0, v[1], 0, 0], [0, 0, v[2], 0], [0, 0, 0, 1]])
        elif t == NS + 'rotate':
            v = [float(x) for x in el.text.split()]
            a = v[3] * math.pi / 180.0
            c, s, x, y, z = math.cos(a), math.sin(a), v[0], v[1], v[2]
            m = mul(m, [[c + x*x*(1-c), x*y*(1-c)-z*s, x*z*(1-c)+y*s, 0],
                        [y*x*(1-c)+z*s, c + y*y*(1-c), y*z*(1-c)-x*s, 0],
                        [z*x*(1-c)-y*s, z*y*(1-c)+x*s, c + z*z*(1-c), 0],
                        [0, 0, 0, 1]])
    return m


def load(src):
    root = ET.parse(src).getroot()
    srcmap = {}
    for s in root.iter(NS + 'source'):
        fa = s.find(NS + 'float_array')
        if fa is not None:
            srcmap[s.get('id')] = [float(x) for x in fa.text.split()]

    geoms = {}
    for g in root.iter(NS + 'geometry'):
        mesh = g.find(NS + 'mesh')
        if mesh is None:
            continue
        pos = None
        for v in mesh.iter(NS + 'vertices'):
            for i in v.iter(NS + 'input'):
                if i.get('semantic') == 'POSITION':
                    pos = srcmap.get(i.get('source').lstrip('#'))
        if not pos:
            continue
        tris = []
        for prim in mesh:
            if prim.tag not in (NS + 'triangles', NS + 'polylist'):
                continue
            off = 0
            for i in prim.iter(NS + 'input'):
                if i.get('semantic') == 'VERTEX':
                    off = int(i.get('offset', 0))
            vsrc = prim.find(NS + 'input')
            if vsrc is None:
                continue
            sid = vsrc.get('source').lstrip('#')
            for acc in prim.iter(NS + 'input'):
                if acc.get('semantic') == 'VERTEX':
                    sid = acc.get('source').lstrip('#')
            stride = None
            for s in root.iter(NS + 'source'):
                if s.get('id') == sid:
                    a = s.find(NS + 'technique_common/' + NS + 'accessor')
                    if a is not None:
                        stride = int(a.get('stride'))
            p = prim.find(NS + 'p')
            if p is None:
                continue
            idx = [int(x) for x in p.text.split()]
            st = stride or 1
            for k in range(0, len(idx) - 2, 3):
                a, b, c = idx[k], idx[k + 1], idx[k + 2]
                try:
                    tris.append((pos[a*st], pos[a*st+1], pos[a*st+2],
                                 pos[b*st], pos[b*st+1], pos[b*st+2],
                                 pos[c*st], pos[c*st+1], pos[c*st+2]))
                except IndexError:
                    pass
        geoms[g.get('id')] = tris

    parts = []

    def walk(node, acc):
        m = mul(node_matrix(node), acc)
        for inst in node.findall(NS + 'instance_geometry'):
            tris = geoms.get(inst.get('url', '').lstrip('#'))
            if not tris:
                continue
            wt = []
            for t in tris:
                # each triangle contributes 3 vertices of (x,y,z); transform each
                # vertex by the world matrix as a COLUMN vector: out[r] = sum_c
                # m[r][c]*v[c] + m[r][3]
                for c in range(3):
                    x, y, z = t[c*3], t[c*3+1], t[c*3+2]
                    wt.append((
                        m[0][0]*x + m[0][1]*y + m[0][2]*z + m[0][3],
                        m[1][0]*x + m[1][1]*y + m[1][2]*z + m[1][3],
                        m[2][0]*x + m[2][1]*y + m[2][2]*z + m[2][3]))
            xs = [p[0] for p in wt]
            ys = [p[1] for p in wt]
            zs = [p[2] for p in wt]
            parts.append({'tris': wt,
                          'bb': (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)),
                          'url': inst.get('url')})
        for ch in node.findall(NS + 'node'):
            walk(ch, m)

    for vs in root.iter(NS + 'visual_scene'):
        for n in vs.findall(NS + 'node'):
            walk(n, ident())
    return parts


def write_dae(path, parts, name):
    verts, index = [], {}
    plist = []
    for p in parts:
        row = []
        for v in p['tris']:
            key = (round(v[0], 5), round(v[1], 5), round(v[2], 5))
            if key not in index:
                index[key] = len(verts)
                verts.append(key)
            row.append(index[key])
        for k in range(0, len(row) - 2, 3):
            plist.extend([row[k], row[k+1], row[k+2]])
    pos = ' '.join(f'{c}' for v in verts for c in v)
    pstr = ' '.join(str(i) for i in plist)
    xml = f'''<?xml version="1.0"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">
  <asset><up_axis>Z_UP</up_axis><unit meter="1" name="inch"/></asset>
  <library_geometries>
    <geometry id="{name}">
      <mesh>
        <source id="{name}_pos">
          <float_array id="{name}_pos_a" count="{len(verts)*3}">{pos}</float_array>
          <technique_common>
            <accessor source="#{name}_pos_a" count="{len(verts)}" stride="3">
              <param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/>
            </accessor>
          </technique_common>
        </source>
        <vertices id="{name}_v"><input semantic="POSITION" source="#{name}_pos"/></vertices>
        <triangles count="{len(plist)//3}">
          <input semantic="VERTEX" source="#{name}_v" offset="0"/>
          <p>{pstr}</p>
        </triangles>
      </mesh>
    </geometry>
  </library_geometries>
  <library_visual_scenes>
    <visual_scene id="{name}_vs">
      <node id="{name}_n"><instance_geometry url="#{name}"/></node>
    </visual_scene>
  </library_visual_scenes>
  <scene><instance_visual_scene url="#{name}_vs"/></scene>
</COLLADA>
'''
    path.write_text(xml)
    return len(verts), len(plist) // 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--size')
    ap.add_argument('--out')
    ap.add_argument('--prefix', default='part')
    a = ap.parse_args()
    parts = load(a.src)
    if a.list or not a.size:
        from collections import Counter
        sig = Counter()
        for p in parts:
            x0, x1, y0, y1, z0, z1 = p['bb']
            sig[(round(x1-x0), round(y1-y0), round(z1-z0))] += 1
        print(f'{a.src}: {len(parts)} parts')
        for k, c in sorted(sig.items(), key=lambda t: -t[1]):
            print(f'  size{k} x{c}')
        return 0
    dx, dy, dz = [float(x) for x in a.size.split(',')]
    sel = [p for p in parts
           if abs((p['bb'][1]-p['bb'][0])-dx) < 0.51
           and abs((p['bb'][3]-p['bb'][2])-dy) < 0.51
           and abs((p['bb'][5]-p['bb'][4])-dz) < 0.51]
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    print(f'{len(sel)} parts match size {dx},{dy},{dz}')
    for i, p in enumerate(sel):
        b = p['bb']
        c = ((b[0]+b[1])/2, (b[2]+b[3])/2, (b[4]+b[5])/2)
        f = out / f'{a.prefix}_{i:02d}.dae'
        nv, nt = write_dae(f, [p], f'{a.prefix}_{i:02d}')
        print(f'  {f.name}: centre=({c[0]:.2f},{c[1]:.2f},{c[2]:.2f}) verts={nv} tris={nt}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
