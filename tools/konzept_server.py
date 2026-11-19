# Kleiner lokaler Server fuer die Konzept-Bilder: liefert das Repo statisch aus und
# nimmt per POST /save/<name>.png die gerenderten Bilder entgegen (Ablage in preview/konzept/).
# Start: python tools/konzept_server.py [port]   ->   http://localhost:8765/galerie/konzept/
import http.server
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = os.path.join(REPO, 'preview', 'konzept')


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=REPO, **kw)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_POST(self):
        m = re.fullmatch(r'/save/([A-Za-z0-9_\-]+\.png)', self.path)
        if not m:
            self.send_error(404)
            return
        data = self.rfile.read(int(self.headers.get('Content-Length', '0')))
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, m.group(1)), 'wb') as f:
            f.write(data)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    port = int(os.environ.get('PORT') or (sys.argv[1] if len(sys.argv) > 1 else 8765))
    http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
