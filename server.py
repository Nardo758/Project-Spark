import subprocess
import sys
import os
import signal
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import threading
import json

BACKEND_PORT = 8000
FRONTEND_PORT = 5000

class ProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/') or self.path == '/docs' or self.path == '/openapi.json' or self.path == '/redoc' or self.path == '/health':
            self.proxy_request('GET')
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/api/'):
            self.proxy_request('POST')
        else:
            self.send_error(405)
    
    def do_PUT(self):
        if self.path.startswith('/api/'):
            self.proxy_request('PUT')
        else:
            self.send_error(405)
    
    def do_DELETE(self):
        if self.path.startswith('/api/'):
            self.proxy_request('DELETE')
        else:
            self.send_error(405)
    
    def do_PATCH(self):
        if self.path.startswith('/api/'):
            self.proxy_request('PATCH')
        else:
            self.send_error(405)
    
    def do_OPTIONS(self):
        if self.path.startswith('/api/'):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
        else:
            self.send_error(405)
    
    def proxy_request(self, method):
        backend_url = f'http://localhost:{BACKEND_PORT}{self.path}'
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            headers = {}
            for header in ['Content-Type', 'Authorization', 'Accept']:
                if self.headers.get(header):
                    headers[header] = self.headers.get(header)
            
            req = Request(backend_url, data=body, headers=headers, method=method)
            
            with urlopen(req, timeout=30) as response:
                self.send_response(response.status)
                for header, value in response.headers.items():
                    if header.lower() not in ['transfer-encoding', 'connection']:
                        self.send_header(header, value)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.read())
        except HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                self.wfile.write(e.read())
            except:
                self.wfile.write(json.dumps({'detail': str(e)}).encode())
        except URLError as e:
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'detail': 'Backend unavailable'}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'detail': str(e)}).encode())
    
    def log_message(self, format, *args):
        print(f"[Frontend] {args[0]}")

def run_backend():
    os.chdir('backend')
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    process = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', 'localhost', '--port', str(BACKEND_PORT)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True
    )
    for line in process.stdout:
        print(f"[Backend] {line}", end='')
    return process

def run_frontend():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('0.0.0.0', FRONTEND_PORT), ProxyHandler)
    print(f"[Frontend] Serving on http://0.0.0.0:{FRONTEND_PORT}")
    server.serve_forever()

if __name__ == '__main__':
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    print("Waiting for backend to start...")
    time.sleep(3)
    
    run_frontend()
