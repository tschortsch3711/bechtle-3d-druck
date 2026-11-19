# Fusion-Skript: baut die Merch-Modelle (ueberarbeitete und neue Teile, buendig eingelegte Farben).
# Gemeinsame Basis (Fusion-Helfer, Logo) liegt in models/Mitbringsel/mb_common.py und mb_logo.py.
# Start in Fusion: Dienstprogramme > Add-Ins > Skripte und Add-Ins > "Merch" > Ausfuehren  (baut alles mit Export).
# Ergebnis: export/merch/<name>__<objekt>__<farbe>.stl, <name>.f3d, Vorschau in preview/merch/.
# Danach "python tools/make_3mf_merch.py" fuer die 3MF-Dateien.
# Parameter stehen jeweils oben in den me_*.py-Dateien.
import importlib
import os
import sys
import time
import traceback

import adsk.core

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))

# Schluessel -> Modul
MODULE = [
    ('muenze', 'me_muenze'),
    ('untersetzer', 'me_untersetzer'),
    ('handystaender', 'me_handystaender'),
    ('wuerfel', 'me_wuerfel'),
    ('lineal', 'me_lineal'),
    ('stiftehalter', 'me_stiftehalter'),
    ('drehzaehler', 'me_drehzaehler'),
    ('zahnrad', 'me_zahnrad'),
]


def bauen(keys=None, nur=None, export=True, offen=False):
    """Baut die Module keys (Liste oder None = alle). nur: Liste von Teilstrings, die im Variantennamen
    vorkommen muessen (None = alle Varianten). Gibt das Protokoll als Text zurueck."""
    # Sperre: Fusion kann nur einen Bau gleichzeitig (Vorschaubilder nutzen das aktive Fenster).
    t0 = getattr(sys, '_merch_sperre', 0)
    if t0 and time.time() - t0 < 900:
        return 'BELEGT: ein anderer Bau laeuft gerade. In 20 Sekunden noch einmal versuchen.'
    sys._merch_sperre = time.time()
    lines = []
    try:
        app = adsk.core.Application.get()
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import me_common
        importlib.reload(me_common.C)
        importlib.reload(me_common.mb_logo)
        importlib.reload(me_common)

        def log(*a):
            lines.append(' '.join(str(x) for x in a))

        out = {'export': os.path.join(REPO, 'export', 'merch') if export else None,
               'preview': os.path.join(REPO, 'preview', 'merch')}
        for d in out.values():
            if d:
                os.makedirs(d, exist_ok=True)
        if isinstance(keys, str):
            keys = [keys]
        if isinstance(nur, str):
            nur = [nur]
        for key, modname in MODULE:
            if keys and key not in keys:
                continue
            log('== %s' % key)
            try:
                mod = importlib.import_module(modname)
                importlib.reload(mod)
                mod.build(app, log, out, nur)
                log('OK %s' % key)
            except Exception:
                log('FEHLER %s\n%s' % (key, traceback.format_exc()))
            finally:
                if not offen:
                    for doc in me_common.OFFEN:
                        try:
                            if doc.isValid:
                                doc.close(False)
                        except Exception:
                            pass
                me_common.OFFEN[:] = []
        log('FERTIG')
    finally:
        sys._merch_sperre = 0
        with open(os.path.join(HERE, 'last_run_%s.log' % ('_'.join(keys) if keys else 'alle')), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
    return '\n'.join(lines)


def run(context):
    bauen(None, export=True)
