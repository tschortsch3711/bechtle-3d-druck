"""Gemeinsame 3MF-Bausteine (Bambu Studio): STL lesen, Objekte mit einem Teil je Farbe schreiben.
Genutzt von make_3mf_merch.py und make_3mf_platten.py.
"""
import os
import uuid
import zipfile
from xml.sax.saxutils import escape

from stl_info import read_stl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EXPORT = os.path.join(ROOT, 'export')
BED_CENTER = (128.0, 128.0)   # X1C: 256 x 256 mm


NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
      'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" '
      'requiredextensions="p"')


def mesh_xml(tris, offset):
    idx = {}
    verts = []
    faces = []
    for t in tris:
        f = []
        for p in t:
            key = (round(p[0] + offset[0], 5), round(p[1] + offset[1], 5), round(p[2] + offset[2], 5))
            i = idx.get(key)
            if i is None:
                i = len(verts)
                idx[key] = i
                verts.append(key)
            f.append(i)
        if len(set(f)) == 3:
            faces.append(f)
    out = ['<mesh><vertices>']
    out += ['<vertex x="%g" y="%g" z="%g"/>' % v for v in verts]
    out.append('</vertices><triangles>')
    out += ['<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(f) for f in faces]
    out.append('</triangles></mesh>')
    return ''.join(out), len(verts), len(faces)


def build(name, objects):
    loaded = []
    for obj_name, parts in objects:
        loaded.append((obj_name, [(read_stl(os.path.join(EXPORT, f)), f, pn, ex) for f, pn, ex in parts]))
    # alles gemeinsam auf die Bettmitte schieben, Unterkante auf z = 0
    allp = [p for _, parts in loaded for tris, *_ in parts for t in tris for p in t]
    mnx, mxx = min(p[0] for p in allp), max(p[0] for p in allp)
    mny, mxy = min(p[1] for p in allp), max(p[1] for p in allp)
    mnz = min(p[2] for p in allp)
    off = (BED_CENTER[0] - (mnx + mxx) / 2.0, BED_CENTER[1] - (mny + mxy) / 2.0, -mnz)

    next_id = 1
    part_objs = []      # (id, xml)
    assemblies = []     # (id, obj_name, [(part_id, part_name, extruder, file)])
    for obj_name, parts in loaded:
        plist = []
        for tris, f, pn, ex in parts:
            m, nv, nf = mesh_xml(tris, off)
            pid = next_id
            next_id += 1
            part_objs.append((pid, '<object id="%d" p:UUID="%s" type="model">%s</object>' % (pid, uuid.uuid4(), m)))
            plist.append((pid, pn, ex, f))
            print('  %-42s %6d Ecken %6d Dreiecke  Filament %d' % (f, nv, nf, ex))
        assemblies.append((next_id, obj_name, plist))
        next_id += 1

    obj_path = '/3D/Objects/object_1.model'
    objects_model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" %s>'
                     '<metadata name="BambuStudio:3mfVersion">1</metadata><resources>%s</resources><build/></model>'
                     % (NS, ''.join(x for _, x in part_objs)))
    res, items = [], []
    for aid, obj_name, plist in assemblies:
        comps = ''.join('<component p:path="%s" objectid="%d" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>'
                        % (obj_path, pid, uuid.uuid4()) for pid, *_ in plist)
        res.append('<object id="%d" p:UUID="%s" type="model"><components>%s</components></object>'
                   % (aid, uuid.uuid4(), comps))
        items.append('<item objectid="%d" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 0 0 0" printable="1"/>'
                     % (aid, uuid.uuid4()))
    main_model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" %s>'
                  '<metadata name="Application">BambuStudio-02.00.00.00</metadata>'
                  '<metadata name="BambuStudio:3mfVersion">1</metadata>'
                  '<metadata name="Title">%s</metadata>'
                  '<resources>%s</resources><build p:UUID="%s">%s</build></model>'
                  % (NS, escape(name), ''.join(res), uuid.uuid4(), ''.join(items)))

    cfg = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>']
    for aid, obj_name, plist in assemblies:
        cfg.append('  <object id="%d">' % aid)
        cfg.append('    <metadata key="name" value="%s"/>' % escape(obj_name))
        cfg.append('    <metadata key="extruder" value="%d"/>' % plist[0][2])
        for pid, pn, ex, f in plist:
            cfg.append('    <part id="%d" subtype="normal_part">' % pid)
            cfg.append('      <metadata key="name" value="%s"/>' % escape(pn))
            cfg.append('      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>')
            cfg.append('      <metadata key="source_file" value="%s"/>' % escape(f))
            cfg.append('      <metadata key="extruder" value="%d"/>' % ex)
            cfg.append('    </part>')
        cfg.append('  </object>')
    cfg.append('  <plate>')
    cfg.append('    <metadata key="plater_id" value="1"/>')
    cfg.append('    <metadata key="plater_name" value=""/>')
    cfg.append('    <metadata key="locked" value="false"/>')
    for n, (aid, *_r) in enumerate(assemblies):
        cfg.append('    <model_instance>')
        cfg.append('      <metadata key="object_id" value="%d"/>' % aid)
        cfg.append('      <metadata key="instance_id" value="0"/>')
        cfg.append('      <metadata key="identify_id" value="%d"/>' % (100 + n))
        cfg.append('    </model_instance>')
    cfg.append('  </plate>')
    cfg.append('</config>')

    content_types = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
                     '<Default Extension="png" ContentType="image/png"/>'
                     '<Default Extension="config" ContentType="text/xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
            '</Relationships>')
    model_rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  '<Relationship Target="%s" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
                  '</Relationships>' % obj_path)

    out = os.path.join(EXPORT, name + '.3mf')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', main_model)
        z.writestr('3D/_rels/3dmodel.model.rels', model_rels)
        z.writestr('3D/Objects/object_1.model', objects_model)
        z.writestr('Metadata/model_settings.config', '\n'.join(cfg) + '\n')
    print('->', os.path.relpath(out, ROOT))
    return out

