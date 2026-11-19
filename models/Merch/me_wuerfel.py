# Deploy-Wuerfel: Entscheidungswuerfel 30 x 30 x 30 mm mit sechs buendig eingelegten Seiten.
# Fuenf Seiten tragen ein rundes dunkelgruenes Feld mit weissem Wort (und teils neongruener zweiter Zeile),
# die sechste Seite (beim Druck unten) das Bechtle-Emblem (Variante logo) oder "KAFFEE / zuerst" (neutral).
#
# Druck: ein Objekt "wuerfel", steht mit der Unterseite auf z = 0, ohne Stuetzen.
#   Farben: weiss (Koerper samt Buchstaben), dunkel (Felder), neon (zweite Zeile), mittel (nur Emblem).
#   Die Unterseite liegt in den ersten drei Schichten (gespiegelt eingelegt), die Oberseite in den letzten drei,
#   die vier Waende sind 0,8 mm tief eingelegt. Oben / unten bleibt es bei 0,6 mm: eingelegt ist nur Dunkel
#   und Neon ueber dem weissen Koerper (die weissen Buchstaben sind der Koerper selbst), nichts Helles ueber Dunkel.
#   Slicer: Arachne-Waende (Details ab 0,45 mm), genug Spuelvolumen von Dunkelgruen nach Weiss,
#   erste Schicht langsam und nicht zu stark gequetscht (Variante neutral hat unten Text).
# Kanten: 8 Kanten (4 senkrechte, 4 obere) sind mit r verrundet. Die 4 unteren Kanten haben dieselbe Rundung
#   nur bis 45 Grad, darunter laeuft sie als 45-Grad-Fase tangential bis zum Bett aus (druckbar ohne Stuetzen,
#   weicht hoechstens 0,27 mm von der vollen Rundung ab, der Wuerfel rollt damit praktisch gleich).
# Felder: 25 mm Durchmesser, damit ROLLBACK einzeilig auf 3,2 mm Versalhoehe kommt. Sie reichen 0,5 mm in die
#   Kantenrundung und werden deshalb mit dem Wuerfel verschnitten (bleiben buendig mit der Rundung).
#   Das Feld der Oberseite hat nur 24,5 mm: so bleibt in der letzten Schicht (Schnitt bei z = 29,9) an den vier
#   engsten Stellen ein 0,52 mm breiter weisser Rand statt 0,26 mm.
# Schrift: Segoe UI fett. Bahnschrift (schmaler, erlaubte groessere Buchstaben) laesst sich in Fusion nicht
#   extrudieren (H, B, K, R haben ueberlappende Konturen).
#   Die Buchstabenecken halten 0,75 mm Abstand zum Feldrand (Schriftkreis 23,5 mm, oben 23,0 mm).
#   Zweite Zeile (heute, hilft, zuerst) bis 4,2 mm Versalhoehe, aber nie groesser als das Hauptwort, mit etwas
#   Zeichenabstand (Luecken r-s, f-t). KAFFEE, REBOOT und ROLLBACK sind ebenfalls leicht gesperrt (K-A, O-O-T,
#   L-L-B), damit die dunklen Luecken zwischen den Buchstaben etwa 0,45 mm oder breiter sind (engste: K-A 0,44 mm).
#   Versalhoehen: SHIP IT 4,25 / heute 4,2, ROLLBACK 3,2, REBOOT / hilft ca. 3,8, TESTEN 4,6, TICKET 4,9,
#   KAFFEE / zuerst ca. 4,0 mm.
# Montage: keine, ein Teil.
import math

import adsk.core
import adsk.fusion

import me_common as M
from me_common import C

WUERFEL = dict(
    kante=30.0,
    r=3.0,                       # Kantenrundung (ebene Flaeche bleibt kante - 2 r = 24 mm)
    feld_d=25.0,                 # rundes Feld (Waende, Unterseite)
    feld_d_oben=24.5,            # Feld der Oberseite: weisser Rand der letzten Schicht bleibt ueber 0,45 mm
    rand=0.75,                   # dunkler Rand zwischen Buchstabenecken und Feldrand
    tiefe_z=0.6,                 # Einlegetiefe oben / unten (3 Schichten)
    tiefe_wand=0.8,              # Einlegetiefe an den Waenden
    font=M.FONT, bold=True,
    cap_einzeilig=5.0,           # groesste Versalhoehe fuer einzeilige Seiten
    zeile1=(4.6, 3.1),           # zweizeilig: groesste Versalhoehe und y der Mitte, Hauptwort
    zeile2=(4.2, -4.1),          # zweizeilig: groesste Versalhoehe und y der Mitte, zweite Zeile (neon)
    abstand_zeile2=8,            # Zeichenabstand der zweiten Zeile (10 = ca. 0,085 x Versalhoehe je Luecke)
    abstand={'KAFFEE': 13,       # Zeichenabstand einzelner Hauptwoerter: K und A beruehren sich sonst
             'REBOOT': 4,        #   (mit 8 noch 0,28 mm am Fuss), O-T und O-O in REBOOT lagen bei 0,36 / 0,42 mm,
             'ROLLBACK': 3},     #   L-L und L-B in ROLLBACK bei 0,40 mm (Versalhoehe bleibt 3,2 mm)
    emblem=21.0,                 # Durchmesser des Emblems auf der Unterseite (Variante logo)
)

# Seite, Hauptwort, zweite Zeile
SEITEN = [
    ('oben', 'SHIP IT', 'heute'),
    ('vorn', 'ROLLBACK', None),
    ('links', 'REBOOT', 'hilft'),
    ('rechts', 'TESTEN', None),
    ('hinten', 'TICKET', None),
]
UNTEN_NEUTRAL = ('unten', 'KAFFEE', 'zuerst')


def _kanten_auf(body, zs):
    """Alle waagerechten Kanten des Koerpers auf den Hoehen zs (mm)."""
    edges = adsk.core.ObjectCollection.create()
    for e in body.edges:
        eb = e.boundingBox
        if abs(eb.minPoint.z - eb.maxPoint.z) > 1e-5:
            continue
        if any(abs(eb.minPoint.z - C.cm(z)) < 1e-5 for z in zs):
            edges.add(e)
    return edges


def _grundkoerper(t, p):
    """Wuerfel mit Rundung r an 8 Kanten und Rundung-plus-Fase an den 4 Bettkanten."""
    s, r = p['kante'], p['r']
    h = s / 2.0
    C.user_param(t.design, 'kante', s, 'Kantenlaenge')
    C.rounded_rect_body(t.root, -h, -h, h, h, r, 'kante', 'wuerfel')
    body = t.root.bRepBodies.itemByName('wuerfel')
    f = r * (2.0 - math.sqrt(2.0))          # Fase, deren Flaeche die Rundung r genau bei 45 Grad beruehrt
    M.fase_kanten(t, body, f, z=0.0)
    body = t.root.bRepBodies.itemByName('wuerfel')
    C.fillet(t.root, _kanten_auf(body, [s, f]), r)
    body = t.root.bRepBodies.itemByName('wuerfel')
    t.log('  Bettkante: Fase %.3f mm + Rundung r %.1f, Standflaeche %.2f mm' % (f, r, s - 2 * f))
    return body


def _cap(t, s, cap_max, y, radius, p, abstand=0):
    """Groesste Versalhoehe (hoechstens cap_max), bei der die Zeile mit Mitte y im Kreis radius bleibt."""
    k = t.text_breite(s, 1.0, p['font'], p['bold'], abstand)
    a = (k * k + 1.0) / 4.0
    yy = abs(y)
    c = (-yy + math.sqrt(yy * yy - 4.0 * a * (yy * yy - radius * radius))) / (2.0 * a)
    return min(cap_max, c)


def _zeile_log(t, p, s, cap, y, ab, strich, kopf):
    """Schreibt Groesse, Zeichenabstand und die aeusserste Ecke (Abstand von der Feldmitte) einer Zeile ins Log."""
    font, bold = p['font'], p['bold']
    w = t.text_breite(s, cap, font, bold, ab)
    luecke = (w - t.text_breite(s, cap, font, bold)) / max(len(s) - 1, 1)
    t.log('    %s%-9s Versalhoehe %.2f mm, Breite %.2f mm, Strich %.2f mm, Zeichenabstand %d (%.2f mm je Luecke), '
          'Ecke bei r %.2f mm' % (kopf, s, cap, w, t.text_breite(strich, cap, font, bold), ab, luecke,
                                  math.hypot(w / 2.0, abs(y) + cap / 2.0)))


def _feld(t, p, haupt, sub, tiefe, feld_d):
    """Rundes Feld mit Text, flach im Ursprung. Rueckgabe: (feld, weisse Buchstaben, neon Buchstaben)."""
    radius = feld_d / 2.0 - p['rand']
    font, bold = p['font'], p['bold']
    feld = t.kreis(feld_d, tiefe=tiefe, farbe='dunkel')
    if sub:
        cmax, y = p['zeile1']
    else:
        cmax, y = p['cap_einzeilig'], 0.0
    ab = p['abstand'].get(haupt, 0)
    cap = _cap(t, haupt, cmax, y, radius, p, ab)
    weiss = t.text(haupt, cap, 0, y, tiefe, 'weiss', font=font, bold=bold, abstand=ab)
    t.log('    Feld %.1f mm, Schriftkreis r %.2f mm' % (feld_d, radius))
    _zeile_log(t, p, haupt, cap, y, ab, 'I', '')
    neon = []
    if sub:
        cmax2, y2 = p['zeile2']
        ab2 = p['abstand_zeile2']
        # nie groesser als das Hauptwort, sonst kippt die Rangfolge der Zeilen (hilft unter REBOOT)
        cap2 = _cap(t, sub, min(cmax2, cap), y2, radius, p, ab2)
        neon = t.text(sub, cap2, 0, y2, tiefe, 'neon', font=font, bold=bold, abstand=ab2)
        _zeile_log(t, p, sub, cap2, y2, ab2, 'l', '/ ')
    return feld, weiss, neon


def _verschneiden(t, bodies, mit):
    """Laesst von den Koerpern nur das stehen, was im Koerper 'mit' liegt (Felder folgen so der Kantenrundung)."""
    comb = t.root.features.combineFeatures
    for b in bodies:
        tc = adsk.core.ObjectCollection.create()
        tc.add(mit)
        ci = comb.createInput(b, tc)
        ci.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
        ci.isKeepToolBodies = True
        comb.add(ci)


def _entfernen(t, bodies):
    """Loescht Hilfskoerper (und meldet sie ab)."""
    for b in bodies:
        t.items = [it for it in t.items if it[0] != b]
        t.root.features.removeFeatures.add(b)


def wuerfel(app, log, out, p, name, logo):
    t = M.Teil(app, log, name)
    t.objekt = 'wuerfel'
    s = p['kante']
    h = s / 2.0
    body = _grundkoerper(t, p)
    t.add(body, 'weiss')

    lage = {'oben': M.oben(s), 'unten': M.unten(0.0),
            'vorn': M.vorn(-h, 0.0, h), 'hinten': M.hinten(h, 0.0, h),
            'links': M.links(-h, 0.0, h), 'rechts': M.rechts(h, 0.0, h)}
    seiten = list(SEITEN) + ([] if logo else [UNTEN_NEUTRAL])
    for seite, haupt, sub in seiten:
        tiefe = p['tiefe_z'] if seite in ('oben', 'unten') else p['tiefe_wand']
        feld_d = p['feld_d_oben'] if seite == 'oben' else p['feld_d']
        feld, weiss, neon = _feld(t, p, haupt, sub, tiefe, feld_d)
        t.auf(lage[seite], feld + weiss + neon)
        if feld_d > s - 2.0 * p['r']:
            _verschneiden(t, feld, body)
        # Buchstaben aus dem Feld schneiden. Die weissen Hilfskoerper werden danach geloescht:
        # beim Einlegen des Feldes bleiben die Buchstaben als Inseln des weissen Wuerfels stehen.
        t.einlegen(feld, weiss + neon)
        _entfernen(t, weiss)
    if logo:
        t.auf(lage['unten'], t.logo('emblem', p['emblem'], 0.0, 0.0, p['tiefe_z']))
    t.einlegen(body, t.koerper('dunkel') + t.koerper('neon') + t.koerper('mittel'))

    t.fertig(out, ansichten=[('', (-78, -107, 70), (0, 0, 1)),
                             ('_hinten', (78, 107, 70), (0, 0, 1)),
                             ('_unten', (0, -75, -150), (0, 0, -1))], rand=1.2)
    return t


def build(app, log, out, nur=None):
    for name, logo in (('wuerfel_logo', True), ('wuerfel_neutral', False)):
        if nur and not any(n in name for n in nur):
            continue
        wuerfel(app, log, out, WUERFEL, name, logo)
