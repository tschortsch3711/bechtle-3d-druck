# Gemeinsame Helfer fuer die Fusion-Skripte. Alle Masse im Code in mm,
# die Fusion-API rechnet intern in cm (Umrechnung nur hier).
import adsk.core
import adsk.fusion
import math

NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation


def cm(v):
    return v / 10.0


def P(x, y, z=0.0):
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))


def V(v_mm):
    return adsk.core.ValueInput.createByReal(cm(v_mm))


def E(expr):
    return adsk.core.ValueInput.createByString(expr)


class Log:
    def __init__(self, path):
        self.path = path
        open(path, 'w', encoding='utf-8').close()

    def __call__(self, *a):
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(' '.join(str(x) for x in a) + '\n')


def new_design(app):
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    return doc, design


def user_param(design, name, value_mm, comment=''):
    ups = design.userParameters
    p = ups.itemByName(name)
    if p:
        p.expression = '%s mm' % value_mm
    else:
        ups.add(name, E('%s mm' % value_mm), 'mm', comment)
    return name


def sub_component(parent_comp, name):
    occ = parent_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ


def offset_plane(comp, expr):
    pi = comp.constructionPlanes.createInput()
    pi.setByOffset(comp.xYConstructionPlane, E(expr))
    return comp.constructionPlanes.add(pi)


def spt(sk, x, y, z=0.0):
    return sk.modelToSketchSpace(P(x, y, z))


def largest_profile(sk):
    best, area = None, -1
    for i in range(sk.profiles.count):
        pr = sk.profiles.item(i)
        a = pr.areaProperties().area
        if a > area:
            best, area = pr, a
    return best


def smallest_profile(sk):
    best, area = None, 1e18
    for i in range(sk.profiles.count):
        pr = sk.profiles.item(i)
        a = pr.areaProperties().area
        if a < area:
            best, area = pr, a
    return best


def fillet(comp, edges, r):
    ff = comp.features.filletFeatures
    fi = ff.createInput()
    try:
        fi.edgeSetInputs.addConstantRadiusEdgeSet(edges, V(r), True)
    except AttributeError:
        fi.addConstantRadiusEdgeSet(edges, V(r), True)
    return ff.add(fi)


def vertical_edges(body):
    edges = adsk.core.ObjectCollection.create()
    for e in body.edges:
        if e.startVertex is None or e.endVertex is None:
            continue
        a = e.startVertex.geometry
        b = e.endVertex.geometry
        if abs(a.x - b.x) < 1e-6 and abs(a.y - b.y) < 1e-6 and abs(a.z - b.z) > 1e-6:
            edges.add(e)
    return edges


def top_face(body):
    best, zmax = None, -1e18
    for f in body.faces:
        pl = adsk.core.Plane.cast(f.geometry)
        if pl is None or abs(abs(pl.normal.z) - 1) > 1e-6:
            continue
        z = f.pointOnFace.z
        if z > zmax:
            best, zmax = f, z
    return best


def chamfer_top(comp, body, d, log=None):
    try:
        f = top_face(body)
        edges = adsk.core.ObjectCollection.create()
        for e in f.edges:
            edges.add(e)
        cf = comp.features.chamferFeatures
        ci = cf.createInput2()
        ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, V(d), True)
        cf.add(ci)
    except Exception as ex:
        if log:
            log('  Hinweis: Fase oben nicht moeglich:', ex)


def rounded_rect_body(comp, x0, y0, x1, y1, r, thick_expr, name, log=None, top_chamfer=0.0):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = name + '_Skizze'
    sk.sketchCurves.sketchLines.addTwoPointRectangle(spt(sk, x0, y0), spt(sk, x1, y1))
    ext = comp.features.extrudeFeatures.addSimple(largest_profile(sk), E(thick_expr), NEW)
    body = ext.bodies.item(0)
    body.name = name
    if r > 0:
        fillet(comp, vertical_edges(body), r)
    body = comp.bRepBodies.itemByName(name)
    if top_chamfer > 0:
        chamfer_top(comp, body, top_chamfer, log)
    return comp.bRepBodies.itemByName(name)


def cut_circle(comp, body, cx, cy, d, depth_mm):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(spt(sk, cx, cy), cm(d / 2.0))
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), CUT)
    ei.startExtent = adsk.fusion.OffsetStartDefinition.create(V(-1))
    ei.setDistanceExtent(False, V(depth_mm + 2))
    ei.participantBodies = [body]
    comp.features.extrudeFeatures.add(ei)


def bbox_mm(bodies):
    xs, ys, zs = [], [], []
    for b in bodies:
        bb = b.boundingBox
        xs += [bb.minPoint.x, bb.maxPoint.x]
        ys += [bb.minPoint.y, bb.maxPoint.y]
        zs += [bb.minPoint.z, bb.maxPoint.z]
    if not xs:
        return None
    return (min(xs) * 10, min(ys) * 10, min(zs) * 10, max(xs) * 10, max(ys) * 10, max(zs) * 10)


def fmt_bb(bb):
    if bb is None:
        return '(leer)'
    return 'x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f  (B %.2f x H %.2f)' % (
        bb[0], bb[3], bb[1], bb[4], bb[2], bb[5], bb[3] - bb[0], bb[4] - bb[1])


_HA = {'left': 'LeftHorizontalAlignment', 'center': 'CenterHorizontalAlignment',
       'right': 'RightHorizontalAlignment'}
_VA = {'top': 'TopVerticalAlignment', 'middle': 'MiddleVerticalAlignment',
       'bottom': 'BottomVerticalAlignment'}


def text_body(comp, plane, z, text, size, box, font, height_expr, name,
              halign='left', valign='middle', bold=False):
    """Extrudierter Text als neue Koerper. box = (x0, y0, x1, y1) in mm, z = Hoehe der Ebene."""
    sk = comp.sketches.add(plane)
    sk.name = name + '_Skizze'
    x0, y0, x1, y1 = box
    ti = sk.sketchTexts.createInput2(text, cm(size))
    ti.setAsMultiLine(spt(sk, x0, y0, z), spt(sk, x1, y1, z),
                      getattr(adsk.core.HorizontalAlignments, _HA[halign]),
                      getattr(adsk.core.VerticalAlignments, _VA[valign]), 0)
    ti.fontName = font
    if bold:
        ti.textStyle = adsk.fusion.TextStyles.TextStyleBold
    st = sk.sketchTexts.add(ti)
    ei = comp.features.extrudeFeatures.createInput(st, NEW)
    ei.setDistanceExtent(False, E(height_expr))
    ext = comp.features.extrudeFeatures.add(ei)
    bodies = [ext.bodies.item(i) for i in range(ext.bodies.count)]
    for i, b in enumerate(bodies):
        b.name = '%s_%d' % (name, i + 1)
    return bodies


def circle_body(comp, plane, z, cx, cy, d, height_expr, name, inner_d=0.0):
    sk = comp.sketches.add(plane)
    sk.name = name + '_Skizze'
    sk.sketchCurves.sketchCircles.addByCenterRadius(spt(sk, cx, cy, z), cm(d / 2.0))
    if inner_d > 0:
        sk.sketchCurves.sketchCircles.addByCenterRadius(spt(sk, cx, cy, z), cm(inner_d / 2.0))
        # Ring = das Profil mit Innenschleife
        prof = None
        for i in range(sk.profiles.count):
            pr = sk.profiles.item(i)
            if pr.profileLoops.count == 2:
                prof = pr
    else:
        prof = sk.profiles.item(0)
    ext = comp.features.extrudeFeatures.addSimple(prof, E(height_expr), NEW)
    b = ext.bodies.item(0)
    b.name = name
    return b


def poly_body(comp, plane, z, pts, height_expr, name):
    """Geschlossener Polygonzug pts = [(x, y), ...] in mm."""
    sk = comp.sketches.add(plane)
    sk.name = name + '_Skizze'
    lines = sk.sketchCurves.sketchLines
    sp = [spt(sk, x, y, z) for x, y in pts]
    first = lines.addByTwoPoints(sp[0], sp[1])
    last = first
    for q in sp[2:]:
        last = lines.addByTwoPoints(last.endSketchPoint, q)
    lines.addByTwoPoints(last.endSketchPoint, first.startSketchPoint)
    ext = comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), E(height_expr), NEW)
    b = ext.bodies.item(0)
    b.name = name
    return b


def arc_band_body(comp, plane, z, center, r_in, r_out, a0_deg, a1_deg, height_expr, name):
    """Kreisringsegment zwischen r_in und r_out von Winkel a0 bis a1 (Grad, gegen den Uhrzeigersinn)."""
    sk = comp.sketches.add(plane)
    sk.name = name + '_Skizze'
    cx, cy = center
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)

    def pt(r, a):
        return spt(sk, cx + r * math.cos(a), cy + r * math.sin(a), z)
    arcs = sk.sketchCurves.sketchArcs
    lines = sk.sketchCurves.sketchLines
    outer = arcs.addByThreePoints(pt(r_out, a0), pt(r_out, (a0 + a1) / 2.0), pt(r_out, a1))
    inner = arcs.addByThreePoints(pt(r_in, a0), pt(r_in, (a0 + a1) / 2.0), pt(r_in, a1))
    for op in (outer.startSketchPoint, outer.endSketchPoint):
        ip = min((inner.startSketchPoint, inner.endSketchPoint),
                 key=lambda q: q.geometry.distanceTo(op.geometry))
        lines.addByTwoPoints(op, ip)
    ext = comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), E(height_expr), NEW)
    b = ext.bodies.item(0)
    b.name = name
    return b


def stroke_body(comp, plane, z, pts, width, height_expr, name):
    """Linienzug mit Strichbreite width (runde Ecken) als ein Koerper."""
    bodies = []
    hw = width / 2.0
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        L = math.hypot(x1 - x0, y1 - y0)
        nx, ny = -(y1 - y0) / L * hw, (x1 - x0) / L * hw
        bodies.append(poly_body(comp, plane, z, [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
                                                 (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)],
                                height_expr, '%s_seg%d' % (name, i)))
    for i, (x, y) in enumerate(pts):
        bodies.append(circle_body(comp, plane, z, x, y, width, height_expr, '%s_knoten%d' % (name, i)))
    tools = adsk.core.ObjectCollection.create()
    for b in bodies[1:]:
        tools.add(b)
    ci = comp.features.combineFeatures.createInput(bodies[0], tools)
    ci.operation = JOIN
    comp.features.combineFeatures.add(ci)
    bodies[0].name = name
    return bodies[0]


def rect_body(comp, plane, z, x0, y0, x1, y1, height_expr, name):
    sk = comp.sketches.add(plane)
    sk.name = name + '_Skizze'
    sk.sketchCurves.sketchLines.addTwoPointRectangle(spt(sk, x0, y0, z), spt(sk, x1, y1, z))
    ext = comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), E(height_expr), NEW)
    b = ext.bodies.item(0)
    b.name = name
    return b


# ---------- Darstellung, Export, Vorschau ----------

_base_appearance = None


def _find_base_appearance(app):
    global _base_appearance
    if _base_appearance is not None:
        return _base_appearance
    fallback = None
    for li in range(app.materialLibraries.count):
        lib = app.materialLibraries.item(li)
        try:
            aps = lib.appearances
        except Exception:
            continue
        for i in range(aps.count):
            a = aps.item(i)
            n = a.name.lower()
            has_color = any(adsk.core.ColorProperty.cast(p) for p in a.appearanceProperties)
            if not has_color:
                continue
            if ('plastic' in n or 'kunststoff' in n) and ('matte' in n or 'matt' in n):
                _base_appearance = a
                return a
            if fallback is None and ('plastic' in n or 'kunststoff' in n):
                fallback = a
    _base_appearance = fallback
    return fallback


def color_appearance(app, design, name, rgb):
    ap = design.appearances.itemByName(name)
    if ap is None:
        base = _find_base_appearance(app)
        if base is None:
            return None
        ap = design.appearances.addByCopy(base, name)
    for p in ap.appearanceProperties:
        cp = adsk.core.ColorProperty.cast(p)
        if cp and cp.isReadOnly is False:
            try:
                cp.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
                break
            except Exception:
                pass
    return ap


def paint(occ, ap):
    if ap is None:
        return
    for b in occ.component.bRepBodies:
        b.appearance = ap


def export_stl(design, geom, path):
    em = design.exportManager
    o = em.createSTLExportOptions(geom, path)
    o.isBinaryFormat = True
    o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    em.execute(o)


def export_f3d(design, path):
    em = design.exportManager
    o = em.createFusionArchiveExportOptions(path, design.rootComponent)
    em.execute(o)


def hide_helpers(design):
    for c in design.allComponents:
        for attr in ('isSketchFolderLightBulbOn', 'isConstructionFolderLightBulbOn',
                     'isOriginFolderLightBulbOn', 'isJointsFolderLightBulbOn'):
            try:
                setattr(c, attr, False)
            except Exception:
                pass


def snapshot(app, path, target, direction, w=1600, h=1100, up=(0, 0, 1), margin=1.25):
    """target in mm, Auge = Ziel + direction (mm)."""
    vp = app.activeViewport
    cam = vp.camera
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    cam.isSmoothTransition = False
    cam.target = P(*target)
    cam.eye = P(target[0] + direction[0], target[1] + direction[1], target[2] + direction[2])
    cam.upVector = adsk.core.Vector3D.create(*up)
    cam.isFitView = True
    vp.camera = cam
    vp.refresh()
    adsk.doEvents()
    # nach dem Einpassen etwas Rand lassen
    cam = vp.camera
    cam.isFitView = False
    cam.viewExtents = cam.viewExtents * margin
    vp.camera = cam
    vp.refresh()
    adsk.doEvents()
    vp.saveAsImageFile(path, w, h)


def rot_x_frame(origin_mm, alpha_deg):
    """Koordinatensystem: lokale X bleibt X, lokale Y kippt um alpha nach hinten (+Y), lokale Z zeigt nach vorn-oben."""
    a = math.radians(alpha_deg)
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(P(*origin_mm),
                              adsk.core.Vector3D.create(1, 0, 0),
                              adsk.core.Vector3D.create(0, math.sin(a), math.cos(a)),
                              adsk.core.Vector3D.create(0, -math.cos(a), math.sin(a)))
    return m
