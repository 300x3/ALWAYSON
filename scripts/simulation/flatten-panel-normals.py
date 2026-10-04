#!/usr/bin/env python3
"""Give every triangle in a planar panel one identical vertex normal.

The CAD export splits each flat panel into several triangles whose three corner
normals differ slightly. Under directional light that produces a smooth gradient
*inside* each triangle, so a flat panel reads as many shaded polygons instead of
one.

This groups triangles that lie on the same plane and writes the group's average
normal into all three corner slots of every triangle in it. Panels then shade as
one flat polygon while still differing from each other, which is what lets the
edge overlay find panel-to-panel boundaries.

The source export is never modified; a derived mesh is written alongside it.
Only the NORMAL <source> float arrays are rewritten - no elements are added or
removed, so the file's structure and namespace handling are left untouched.
"""
import argparse
import collections
import math
import re
import sys
import xml.etree.ElementTree as ET

NS = {'c': 'http://www.collada.org/2005/11/COLLADASchema'}


def face_frame(tri):
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = tri
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    m = math.sqrt(nx * nx + ny * ny + nz * nz)
    if m < 1e-12:
        return None
    nx, ny, nz = nx / m, ny / m, nz / m
    return (nx, ny, nz), nx * ax + ny * ay + nz * az


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('dest')
    ap.add_argument('--angle', type=float, default=0.5, help='degrees')
    ap.add_argument('--dist', type=float, default=0.002, help='metres')
    args = ap.parse_args()

    text = open(args.source).read()
    root = ET.parse(args.source).getroot()
    lib = root.find('c:library_geometries', NS)

    # ---- 1. read positions, triangle indices and the normal source per geom --
    geoms = []
    for g in lib.findall('c:geometry', NS):
        mesh = g.find('c:mesh', NS)
        verts = mesh.find('c:vertices', NS)
        vmap = {i.get('semantic'): i.get('source').lstrip('#')
                for i in verts.findall('c:input', NS)}
        if 'POSITION' not in vmap:
            continue
        if 'NORMAL' not in vmap:
            # A handful of empty/placeholder geometries carry no normal source.
            # They have no triangles either, so there is nothing to flatten.
            if not mesh.findall('c:triangles', NS):
                continue
            sys.exit('geometry %s has triangles but no NORMAL source' % g.get('id'))
        pdef = [s for s in mesh.findall('c:source', NS)
                if s.get('id') == vmap['POSITION']][0]
        P = list(map(float, pdef.find('c:float_array', NS).text.split()))
        sets = []
        for t in mesh.findall('c:triangles', NS):
            cnt = int(t.get('count'))
            p = list(map(int, t.find('c:p', NS).text.split()))
            stride = len(t.findall('c:input', NS))
            sets.append((cnt, p, stride))
        geoms.append({'gid': g.get('id'), 'P': P, 'sets': sets,
                      'nid': vmap['NORMAL']})

    # ---- 2. group triangles onto planes -------------------------------------
    cos_tol = math.cos(math.radians(args.angle))
    planes = []
    buckets = collections.defaultdict(list)
    for gi, G in enumerate(geoms):
        P = G['P']
        for si, (cnt, p, stride) in enumerate(G['sets']):
            if stride != 1:
                sys.exit('unexpected vertex stride %d' % stride)
            for ti in range(cnt):
                tri = [(P[p[i]*3], P[p[i]*3+1], P[p[i]*3+2])
                       for i in (ti*3, ti*3+1, ti*3+2)]
                fr = face_frame(tri)
                if fr is None:
                    planes.append([(0.0, 0.0, 1.0), 0.0, [(gi, si, ti)]])
                    continue
                n, d = fr
                key = (round(n[0], 2), round(n[1], 2), round(n[2], 2))
                for pi in buckets[key]:
                    pl = planes[pi]
                    if (sum(a*b for a, b in zip(n, pl[0])) > cos_tol
                            and abs(d - pl[1]) < args.dist):
                        pl[2].append((gi, si, ti))
                        break
                else:
                    planes.append([n, d, [(gi, si, ti)]])
                    buckets[key].append(len(planes) - 1)

    # ---- 3. one averaged normal per plane -----------------------------------
    plane_normal = []
    for n, d, members in planes:
        sx = sy = sz = 0.0
        for gi, si, ti in members:
            G = geoms[gi]
            P = G['P']
            _, p, _ = G['sets'][si]
            tri = [(P[p[i]*3], P[p[i]*3+1], P[p[i]*3+2])
                   for i in (ti*3, ti*3+1, ti*3+2)]
            fr = face_frame(tri)
            if fr is None:
                continue
            sx += fr[0][0]; sy += fr[0][1]; sz += fr[0][2]
        m = math.sqrt(sx*sx + sy*sy + sz*sz)
        plane_normal.append((sx/m, sy/m, sz/m) if m > 1e-12 else n)

    # ---- 4. build a replacement NORMAL array for each geometry ---------------
    new_normals = {}
    for gi, G in enumerate(geoms):
        new_normals[G['nid']] = [None] * (len(G['P']) // 3)

    for pi, (_, _, members) in enumerate(planes):
        nrm = plane_normal[pi]
        for gi, si, ti in members:
            G = geoms[gi]
            _, p, _ = G['sets'][si]
            arr = new_normals[G['nid']]
            for k in range(3):
                v = p[ti*3 + k]
                arr[v] = nrm

    # any slot never referenced by a triangle keeps its original value
    nsrc_vals = {}
    for s in lib.findall('c:geometry', NS):
        pass
    for g in lib.iter('{%s}source' % NS['c']):
        sid = g.get('id')
        if sid in new_normals:
            nsrc_vals[sid] = list(map(float, g.find('c:float_array', NS).text.split()))

    for sid, arr in new_normals.items():
        orig = nsrc_vals[sid]
        for v, nrm in enumerate(arr):
            if nrm is None:
                base = orig[v*3:v*3+3] or [0.0, 0.0, 1.0]
                arr[v] = (base[0], base[1], base[2])
        new_normals[sid] = arr

    # ---- 5. splice the new arrays into the raw text, last span first --------
    spans = []
    for m in re.finditer(r'<source\b[^>]*id="([^"]+)"[^>]*>(.*?)</source>', text, re.S):
        sid = m.group(1)
        if sid not in new_normals:
            continue
        fa = re.search(r'(<float_array\b[^>]*>)(.*?)(</float_array>)', m.group(2), re.S)
        if not fa:
            sys.exit('no float_array in source %s' % sid)
        start = m.start(2) + fa.start(2)
        end = m.start(2) + fa.end(2)
        spans.append((start, end, sid))

    out = text
    for start, end, sid in sorted(spans, reverse=True):
        body = ' '.join(f'{v:.6f}' for n in new_normals[sid] for v in n)
        out = out[:start] + body + out[end:]

    open(args.dest, 'w').write(out)

    ntri = sum(c for G in geoms for c, _, _ in G['sets'])
    print(f'triangles: {ntri}  ->  {len(planes)} planar groups')
    print(f'rewrote {len(spans)} NORMAL arrays')
    print(f'wrote {args.dest}')


if __name__ == '__main__':
    main()
