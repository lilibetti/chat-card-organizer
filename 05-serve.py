"""
05-serve.py
===========

Start a local HTTP server so the three HTML pages can fetch the
JSON files via `fetch()`. Browsers refuse to read local files over
the `file://` protocol, so opening the HTML by double-click won't
work — the server is required.

Usage
-----
    python 05-serve.py           # default port 8000
    python 05-serve.py 8765      # custom port
"""
import os
import sys
import http.server
import socketserver
import threading
import webbrowser

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DIR)
URL = f"http://localhost:{PORT}/browse.html"


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # quiet


def open_browser():
    webbrowser.open(URL)


print("server running:")
print(f"  {URL}")
print(f"  http://localhost:{PORT}/conversation.html")
print(f"  http://localhost:{PORT}/collections.html")
print(f"  serving from: {DIR}")
print("  Ctrl+C to stop")

# Wait a second before opening the browser so the server is ready
# when the first request lands.
threading.Timer(1.0, open_browser).start()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
