# Gemeinsame Helfer fuer die Merch-Modelle. Baut auf models/Mitbringsel/mb_common.py auf (dort: mm im Code, cm in der API).
#
# Prinzip "buendig eingelegt":
#   1. Grundkoerper bauen und mit t.add(koerper, farbe) anmelden.
#   2. Grafik (Text, Logo, Formen) entsteht immer flach im Ursprung: lokale Ebene XY, Koerper von z = -tiefe bis 0.
#   3. t.auf(flaeche, koerper) legt die Grafik auf eine Flaeche des Teils (z = 0 der Grafik = Oberflaeche, -z = ins Material).
#   4. t.einlegen(wirt, grafik) schneidet die Grafik aus dem Wirt heraus, die Grafik bleibt als eigener Koerper stehen.
#   5. t.fertig(out) faerbt ein, schreibt je Objekt und Farbe eine STL, die F3D und die Vorschaubilder.
import math
import os
import struct
import sys
import glob

import adsk.core
import adsk.fusion

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
_MB = os.path.join(REPO, 'models', 'Mitbringsel')
if _MB not in sys.path:
    sys.path.insert(0, _MB)
import mb_common as C      # noqa: E402
import mb_logo             # noqa: E402

LOGO_SVG = os.path.join(_MB, 'logo', 'Logo_Bechtle.svg')

# Offizielle Bechtle-Farben plus neutrale Toene. Reihenfolge = Filament-Nummer in der 3MF.
FARBEN = {
    'weiss': (243, 243, 239),
    'dunkel': (7, 80, 51),        # Experience Green #075033
    'mittel': (35, 169, 106),     # Progressive Green #23A96A
    'neon': (47, 251, 149),       # Future Green #2FFB95
    'anthrazit': (43, 52, 66),
    'schwarz': (24, 24, 24),
    'grau': (150, 156, 163),
    'rot': (200, 50, 40),
    'gelb': (240, 180, 30),
}
FILAMENT = list(FARBEN.keys())

FONT = 'Segoe UI'              # mit bold=True
FONT_BLACK = 'Segoe UI Black'  # sehr fett, fuer Ziffern und kurze Woerter (bold=False)
FONT_SEMI = 'Segoe UI Semibold'
FONT_MONO = 'Consolas'         # mit bold=True

OFFEN = []       # in diesem Lauf geoeffnete Dokumente (der Starter schliesst sie)


def _vec(t):
    return adsk.core.Vector3D.create(float(t[0]), float(t[1]), float(t[2]))


def _liste(x):
    if x is None:
        return []
    if isinstance(x, (list, tuple)):
        out = []
        for e in x:
            out += _liste(e)
        return out
    return [x]


def flaeche(ursprung, u, v):
    """Lage einer Flaeche: ursprung in mm, u = lokale x-Richtung (nach rechts), v = lokale y-Richtung (nach oben).
    Die Normale u x v zeigt aus dem Teil heraus."""
    uu, vv = _vec(u), _vec(v)
    uu.normalize()
    vv.normalize()
    n = uu.crossProduct(vv)
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(C.P(*ursprung), uu, vv, n)
    return m


def oben(z, x=0.0, y=0.0):
    return flaeche((x, y, z), (1, 0, 0), (0, 1, 0))


def unten(z=0.0, x=0.0, y=0.0):
    """Unterseite, von unten gelesen (gespiegelt eingelegt, erste Druckschichten)."""
    return flaeche((x, y, z), (-1, 0, 0), (0, 1, 0))


def vorn(y, x=0.0, z=0.0):
    """Senkrechte Flaeche, die nach -Y schaut. Lokales y = Welt-Z."""
    return flaeche((x, y, z), (1, 0, 0), (0, 0, 1))


def hinten(y, x=0.0, z=0.0):
    return flaeche((x, y, z), (-1, 0, 0), (0, 0, 1))


def links(x, y=0.0, z=0.0):
    return flaeche((x, y, z), (0, -1, 0), (0, 0, 1))


def rechts(x, y=0.0, z=0.0):
    return flaeche((x, y, z), (0, 1, 0), (0, 0, 1))


class Teil:
    """Ein Fusion-Dokument mit Koerpern, die je einer Farbe und einem Druckobjekt zugeordnet sind."""

    def __init__(self, app, log, name):
        self.app, self.log, self.name = app, log, name
        self.doc, self.design = C.new_design(app)
        OFFEN.append(self.doc)
        self.root = self.design.rootComponent
        self.xy = self.root.xYConstructionPlane
        self.items = []          # [koerper, farbe, objekt]
        self.objekt = 'teil'     # aktuelles Druckobjekt fuer add()
        self._n = 0
        self._kal = {}
        log('-- %s' % name)

    # ---------- Verwaltung ----------
    def _nm(self, prefix='k'):
        self._n += 1
        return '%s%03d' % (prefix, self._n)

    def add(self, koerper, farbe, objekt=None):
        """Meldet Koerper mit Farbe an (und Druckobjekt, sonst self.objekt)."""
        assert farbe in FARBEN, 'unbekannte Farbe %s' % farbe
        out = _liste(koerper)
        for b in out:
            self.items.append([b, farbe, objekt or self.objekt])
        return out

    def koerper(self, farbe=None, objekt=None):
        return [b for b, f, o in self.items if (farbe is None or f == farbe) and (objekt is None or o == objekt)]

    def _eintrag(self, body):
        for it in self.items:
            if it[0] == body:
                return it
        return None

    def umfaerben(self, koerper, farbe):
        for b in _liste(koerper):
            it = self._eintrag(b)
            if it:
                it[1] = farbe

    # ---------- Lage ----------
    def auf(self, matrix, koerper):
        """Bewegt Koerper mit einer Matrix (siehe flaeche(), oben(), unten(), vorn() ...)."""
        bodies = _liste(koerper)
        if not bodies:
            return bodies
        col = adsk.core.ObjectCollection.create()
        for b in bodies:
            col.add(b)
        mf = self.root.features.moveFeatures
        mi = mf.createInput2(col)
        mi.defineAsFreeMove(matrix)
        mf.add(mi)
        return bodies

    def einlegen(self, wirte, grafik):
        """Schneidet die Grafik-Koerper aus den Wirten (Grafik bleibt erhalten). Entstehen dabei neue
        Koerper (Wirt zerfaellt), erben sie Farbe und Objekt des Wirts."""
        tools = [t for t in _liste(grafik)]
        comb = self.root.features.combineFeatures
        for h in _liste(wirte):
            hb = h.boundingBox
            tc = adsk.core.ObjectCollection.create()
            for t in tools:
                if t != h and hb.intersects(t.boundingBox):
                    tc.add(t)
            if tc.count == 0:
                continue
            vor = [b for b in self.root.bRepBodies]
            ci = comb.createInput(h, tc)
            ci.operation = C.CUT
            ci.isKeepToolBodies = True
            try:
                comb.add(ci)
            except RuntimeError as ex:
                self.log('  Hinweis: Einlegen in %s uebersprungen (%s)' % (h.name, str(ex).splitlines()[0]))
                continue
            if self.root.bRepBodies.count != len(vor):
                it = self._eintrag(h)
                for b in self.root.bRepBodies:
                    if not any(b == v for v in vor):
                        self.items.append([b, it[1] if it else 'weiss', it[2] if it else self.objekt])

    # ---------- Grafik: entsteht im Ursprung, z = -tiefe .. 0 ----------
    def _expr(self, tiefe):
        return '%g mm' % (-tiefe)

    def kreis(self, d, x=0.0, y=0.0, tiefe=0.6, farbe='dunkel', innen_d=0.0):
        """Kreisscheibe oder (mit innen_d) Ring."""
        b = C.circle_body(self.root, self.xy, 0, x, y, d, self._expr(tiefe), self._nm('kreis'), inner_d=innen_d)
        return self.add(b, farbe)

    def rechteck(self, x0, y0, x1, y1, tiefe=0.6, farbe='dunkel', r=0.0):
        if r > 0:
            b = C.rounded_rect_body(self.root, x0, y0, x1, y1, r, self._expr(tiefe), self._nm('rechteck'))
        else:
            b = C.rect_body(self.root, self.xy, 0, x0, y0, x1, y1, self._expr(tiefe), self._nm('rechteck'))
        return self.add(b, farbe)

    def poly(self, pts, tiefe=0.6, farbe='dunkel'):
        b = C.poly_body(self.root, self.xy, 0, pts, self._expr(tiefe), self._nm('poly'))
        return self.add(b, farbe)

    def linie(self, pts, breite=1.0, tiefe=0.6, farbe='dunkel'):
        """Linienzug mit runden Enden, Strichbreite in mm."""
        b = C.stroke_body(self.root, self.xy, 0, pts, breite, self._expr(tiefe), self._nm('linie'))
        return self.add(b, farbe)

    def bogen(self, r_innen, r_aussen, a0, a1, tiefe=0.6, farbe='dunkel', x=0.0, y=0.0):
        """Kreisringsegment von Winkel a0 bis a1 (Grad, gegen den Uhrzeigersinn)."""
        b = C.arc_band_body(self.root, self.xy, 0, (x, y), r_innen, r_aussen, a0, a1, self._expr(tiefe), self._nm('bogen'))
        return self.add(b, farbe)

    def _text_skizze(self, s, cap, font, bold, x0, y0, abstand=0):
        sk = self.root.sketches.add(self.xy)
        ti = sk.sketchTexts.createInput2(s, C.cm(cap))
        ti.setAsMultiLine(C.P(x0, y0), C.P(x0 + max(50.0, len(s) * cap * 3.0), y0 + cap * 3.0),
                          adsk.core.HorizontalAlignments.LeftHorizontalAlignment,
                          adsk.core.VerticalAlignments.BottomVerticalAlignment, abstand)
        ti.fontName = font
        if bold:
            ti.textStyle = adsk.fusion.TextStyles.TextStyleBold
        return sk, sk.sketchTexts.add(ti)

    def text_breite(self, s, cap, font=FONT, bold=True, abstand=0):
        """Breite des gesetzten Textes in mm (Versalhoehe cap)."""
        b = self._messen(s, cap, font, bold, abstand)
        return b[2] - b[0]

    def _messen(self, s, cap, font, bold, abstand=0):
        key = (s, font, bold, abstand)
        if key not in self._kal:
            sk, st = self._text_skizze(s, 10.0, font, bold, 0.0, 0.0, abstand)
            bb = st.boundingBox
            self._kal[key] = (bb.minPoint.x * 10, bb.minPoint.y * 10, bb.maxPoint.x * 10, bb.maxPoint.y * 10)
            sk.deleteMe()
        return tuple(v * cap / 10.0 for v in self._kal[key])

    def text(self, s, cap, x=0.0, y=0.0, tiefe=0.6, farbe='dunkel', font=FONT, bold=True,
             max_breite=None, align='mitte', abstand=0):
        """Text mit Versalhoehe cap (mm). (x, y) = Mitte der Versalhoehe; align 'mitte' | 'links' | 'rechts'.
        max_breite verkleinert den Text, bis er passt. abstand = zusaetzlicher Zeichenabstand (10 entspricht
        etwa 0,085 x Versalhoehe je Luecke), z. B. damit sich Buchstaben wie R und A nicht beruehren.
        Rueckgabe: Koerper (einer je Buchstabenteil)."""
        bb = self._messen(s, cap, font, bold, abstand)
        w = bb[2] - bb[0]
        if max_breite and w > max_breite:
            cap *= max_breite / w
            bb = self._messen(s, cap, font, bold, abstand)
        if align == 'mitte':
            x0 = x - (bb[0] + bb[2]) / 2.0
        elif align == 'links':
            x0 = x - bb[0]
        else:
            x0 = x - bb[2]
        sk, st = self._text_skizze(s, cap, font, bold, x0, y - cap / 2.0, abstand)
        sk.name = self._nm('text') + '_Skizze'
        return self._text_extrudieren(st, tiefe, farbe)

    # Zeichenabstand am Bogen: 100 Einheiten weiten jede Luecke um etwa 0,84 x Versalhoehe.
    ABSTAND_JE_100 = 0.84

    def bogen_abstand(self, s, cap, radius, font=FONT, bold=True):
        """Zeichenabstand fuer einen unteren Bogentext (Koepfe zur Mitte): gleicht aus, dass die Buchstaben
        an den Koepfen zusammenlaufen, und laesst dort etwas mehr Luft als im geraden Satz."""
        n = max(len(s), 2)
        rb = radius + cap / 2.0
        vorschub = self.text_breite(s, 1.0, font, bold) / n          # mittlere Zeichenbreite je mm Versalhoehe
        return int(round(100.0 * vorschub * (cap / rb) / self.ABSTAND_JE_100)) + 12

    def bogen_breite(self, s, cap, font=FONT, bold=True, abstand=0):
        """Laenge eines Bogentextes auf der Grundlinie in mm."""
        return (self.text_breite(s, 1.0, font, bold) + (len(s) - 1) * self.ABSTAND_JE_100 * abstand / 100.0) * cap

    def _text_extrudieren(self, st, tiefe, farbe):
        ext = self.root.features.extrudeFeatures
        ei = ext.createInput(st, C.NEW)
        ei.setDistanceExtent(False, C.V(-tiefe))
        e = ext.add(ei)
        bodies = [e.bodies.item(i) for i in range(e.bodies.count)]
        nm = self._nm('text')
        for i, b in enumerate(bodies):
            b.name = '%s_%d' % (nm, i + 1)
        return self.add(bodies, farbe)

    def bogentext(self, s, cap, radius, oben=True, tiefe=0.6, farbe='dunkel', font=FONT, bold=True,
                  max_winkel=None, x=0.0, y=0.0, abstand=None):
        """Text auf einem Kreisbogen um (x, y). radius = Mitte der Versalhoehe.
        oben=True: Text steht oben und liest sich im Uhrzeigersinn; oben=False: Text steht unten, Koepfe zur Mitte.
        max_winkel (Grad) verkleinert den Text, bis er passt.
        abstand = Zeichenabstand; None: oben 0, unten automatisch (siehe bogen_abstand), damit die Buchstaben
        an den Koepfen nicht verschmelzen."""
        if abstand is None:
            abstand = 0 if oben else self.bogen_abstand(s, cap, radius, font, bold)
        w = self.bogen_breite(s, cap, font, bold, abstand)
        rb = radius - cap / 2.0 if oben else radius + cap / 2.0     # Grundlinie
        if max_winkel and math.degrees(w / rb) > max_winkel:
            cap *= math.radians(max_winkel) * rb / w
            rb = radius - cap / 2.0 if oben else radius + cap / 2.0
        if oben:
            pts = [(-rb, 0.0), (0.0, rb), (rb, 0.0)]
        else:
            pts = [(-rb, 0.0), (0.0, -rb), (rb, 0.0)]
        # Scheitert die Extrusion (Buchstaben beruehren sich), mit mehr Zeichenabstand noch einmal versuchen.
        for abstand in (abstand, abstand + 8, abstand + 16, abstand + 26, abstand + 40):
            sk = self.root.sketches.add(self.xy)
            sk.name = self._nm('bogentext') + '_Skizze'
            arc = sk.sketchCurves.sketchArcs.addByThreePoints(*[C.P(x + px, y + py) for px, py in pts])
            arc.isConstruction = True
            ti = sk.sketchTexts.createInput2(s, C.cm(cap))
            ti.setAsAlongPath(arc, True, adsk.core.HorizontalAlignments.CenterHorizontalAlignment, abstand)
            ti.fontName = font
            if bold:
                ti.textStyle = adsk.fusion.TextStyles.TextStyleBold
            st = sk.sketchTexts.add(ti)
            try:
                k = self._text_extrudieren(st, tiefe, farbe)
            except RuntimeError:
                sk.deleteMe()
                continue
            self.log('    Bogentext "%s": Versalhoehe %.2f mm, Zeichenabstand %d, %d Koerper'
                     % (s, cap, abstand, len(k)))
            return k
        raise RuntimeError('Bogentext "%s" laesst sich nicht extrudieren' % s)

    _logo_dateien = None

    def logo(self, teil='voll', breite=20.0, x=0.0, y=0.0, tiefe=0.6, mono=None,
             farben=('dunkel', 'mittel'), weiss=None):
        """Bechtle-Logo aus dem SVG. teil: 'emblem' | 'wort' | 'voll'. breite = Breite des gewaehlten Teils,
        (x, y) = dessen Mitte. Seitenverhaeltnis: Emblem ca. 1 : 1, Wortmarke 4,47 : 1, voll 5,04 : 1.
        mono='weiss' setzt alles in einer Farbe (das weisse Feld im Emblem bleibt dann Wirtfarbe).
        weiss='weiss' legt das weisse Feld des Emblems als eigenen Koerper ein (fuer nicht weisse Wirte)."""
        if Teil._logo_dateien is None:
            Teil._logo_dateien = mb_logo._split_svg(LOGO_SVG)
        files = Teil._logo_dateien                      # [(datei, fill)]: Wortmarke, hell, weiss, Emblem dunkel
        wahl = {'emblem': files[1:], 'wort': files[:1], 'voll': files}[teil]
        ref = [f for f, _ in wahl]
        gruppen = {}
        for f, fill in wahl:
            if fill == '#075033':
                farbe = mono or farben[0]
            elif fill == '#23a96a':
                farbe = mono or farben[1]
            else:
                farbe = weiss
            if farbe:
                gruppen.setdefault(farbe, []).append(f)
        out = []
        for farbe, fs in gruppen.items():
            sk = mb_logo._import_fit(self.root, self.xy, fs, ref, x, y, breite, self._nm('logo'), lambda *a: None)
            sel, _holes = mb_logo._filled_profiles(sk)
            e = self.root.features.extrudeFeatures.addSimple(sel, C.V(-tiefe), C.NEW)
            bodies = [e.bodies.item(i) for i in range(e.bodies.count)]
            nm = self._nm('logo')
            for i, b in enumerate(bodies):
                b.name = '%s_%d' % (nm, i + 1)
            out += self.add(bodies, farbe)
        return out

    # ---------- Abschluss ----------
    def _stl(self, bodies, path):
        tris = []
        for b in bodies:
            calc = b.meshManager.createMeshCalculator()
            calc.surfaceTolerance = 0.001                 # 0,01 mm
            calc.maxNormalDeviation = math.radians(8)
            m = calc.calculate()
            co = m.nodeCoordinatesAsDouble
            idx = m.nodeIndices
            for i in range(0, len(idx), 3):
                tris.append(tuple((co[3 * k] * 10.0, co[3 * k + 1] * 10.0, co[3 * k + 2] * 10.0)
                                  for k in (idx[i], idx[i + 1], idx[i + 2])))
        with open(path, 'wb') as f:
            f.write(b'Merch STL (mm)'.ljust(80, b' '))
            f.write(struct.pack('<I', len(tris)))
            for a, b_, c in tris:
                ux, uy, uz = b_[0] - a[0], b_[1] - a[1], b_[2] - a[2]
                vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
                nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
                ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
                f.write(struct.pack('<12fH', nx / ln, ny / ln, nz / ln, *a, *b_, *c, 0))
        return len(tris)

    def bericht(self):
        """Schreibt je Objekt und Farbe Anzahl, Box und Volumen ins Log, dazu Hinweise auf sehr schmale Koerper."""
        self.items = [it for it in self.items if it[0].isValid]
        objekte = []
        for _, _, o in self.items:
            if o not in objekte:
                objekte.append(o)
        for o in objekte:
            bb = C.bbox_mm(self.koerper(objekt=o))
            self.log('  Objekt %s: %.2f x %.2f x %.2f mm (z %.2f .. %.2f)'
                     % (o, bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2], bb[2], bb[5]))
            for f in FILAMENT:
                bs = self.koerper(f, o)
                if not bs:
                    continue
                vol = sum(b.volume for b in bs) * 1000.0
                self.log('    %-9s %3d Koerper  %9.1f mm3' % (f, len(bs), vol))
        schmal = 0
        for b, f, o in self.items:
            bb = C.bbox_mm([b])
            dims = sorted([bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]])
            if dims[1] < 0.45:
                schmal += 1
        if schmal:
            self.log('  Hinweis: %d Koerper sind in zwei Richtungen schmaler als 0,45 mm' % schmal)

    def fertig(self, out, ansichten=None, montage=None, rand=1.15):
        """Faerbt ein, exportiert (Drucklage), ruft optional montage() auf (Teile fuer das Bild zusammensetzen),
        macht Vorschaubilder und schreibt die F3D.
        ansichten: Liste (suffix, richtung_mm, up), Standard: schraeg und von oben."""
        self.items = [it for it in self.items if it[0].isValid]
        for i, (b, f, o) in enumerate(self.items):
            b.appearance = C.color_appearance(self.app, self.design, 'Merch ' + f, FARBEN[f])
            b.name = '%s_%s_%03d' % (o, f, i + 1)
        self.bericht()
        e = out.get('export')
        if e:
            for old in glob.glob(os.path.join(e, self.name + '__*.stl')):
                os.remove(old)
            objekte = []
            for _, _, o in self.items:
                if o not in objekte:
                    objekte.append(o)
            for o in objekte:
                for f in FILAMENT:
                    bs = self.koerper(f, o)
                    if bs:
                        self._stl(bs, os.path.join(e, '%s__%s__%s.stl' % (self.name, o, f)))
        if montage:
            montage()
        if e:
            C.export_f3d(self.design, os.path.join(e, self.name + '.f3d'))
        C.hide_helpers(self.design)
        self.doc.activate()
        bb = C.bbox_mm([it[0] for it in self.items])
        ziel = ((bb[0] + bb[3]) / 2.0, (bb[1] + bb[4]) / 2.0, (bb[2] + bb[5]) / 2.0)
        if ansichten is None:
            ansichten = [('', (-40, -110, 120), (0, 0, 1)), ('_oben', (0, 0, 200), (0, 1, 0))]
        for suffix, richtung, up in ansichten:
            C.snapshot(self.app, os.path.join(out['preview'], self.name + suffix + '.png'), ziel, richtung,
                       up=up, margin=rand)
        self.log('  fertig: %s' % self.name)


def fase_kanten(teil, body, d, nur_kreise=False, z=None):
    """Fase d an allen Kanten der ebenen Deck- und Bodenflaechen (z = None) oder nur auf Hoehe z (mm)."""
    edges = adsk.core.ObjectCollection.create()
    bb = body.boundingBox
    zs = [bb.minPoint.z, bb.maxPoint.z] if z is None else [C.cm(z)]
    for e in body.edges:
        eb = e.boundingBox
        if abs(eb.minPoint.z - eb.maxPoint.z) > 1e-6:
            continue
        if not any(abs(eb.minPoint.z - zz) < 1e-6 for zz in zs):
            continue
        if nur_kreise and adsk.core.Circle3D.cast(e.geometry) is None:
            continue
        edges.add(e)
    cf = teil.root.features.chamferFeatures
    ci = cf.createInput2()
    ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, C.V(d), False)
    cf.add(ci)
