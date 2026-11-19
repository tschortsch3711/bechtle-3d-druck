"""Kurzinfo zu binaeren STL-Dateien: Dreiecke und Bounding-Box (in Datei-Einheiten)."""
import os
import struct
import sys


def read_stl(path):
    with open(path, 'rb') as f:
        data = f.read()
    n = struct.unpack_from('<I', data, 80)[0]
    if 84 + n * 50 != len(data):
        raise ValueError('%s: keine binaere STL (oder beschaedigt)' % path)
    tris = []
    off = 84
    for _ in range(n):
        v = struct.unpack_from('<12f', data, off)
        tris.append((v[3:6], v[6:9], v[9:12]))
        off += 50
    return tris


def bbox(tris):
    xs = [p[0] for t in tris for p in t]
    ys = [p[1] for t in tris for p in t]
    zs = [p[2] for t in tris for p in t]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        t = read_stl(p)
        b = bbox(t)
        print('%-45s %6d Dreiecke  x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f' % (
            os.path.basename(p), len(t), b[0], b[3], b[1], b[4], b[2], b[5]))
