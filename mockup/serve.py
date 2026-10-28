#!/usr/bin/env python3
"""Local mockup server (standard library only).

  python3 mockup/serve.py          # http://localhost:5173
  python3 mockup/serve.py 8000     # another port

Required because the JSON files in data/ do not load when the page is opened via file://.
"""
import functools
import http.server
import sys
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5173
ROOT_DIR = Path(__file__).resolve().parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")  # always show the latest edit
        super().end_headers()


def main():
    handler = functools.partial(Handler, directory=str(ROOT_DIR))
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler) as server:
        print(f"Mockup em http://localhost:{PORT}  (Ctrl+C para parar)")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nEncerrado.")


if __name__ == "__main__":
    main()
