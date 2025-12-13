import subprocess
import sys
import os
import signal
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse, unquote
import threading
import json

def get_frontend_port(default_port: int = 5000) -> int:
    """Return public HTTP port (deployment uses PORT env)."""
    if os.getenv("REPLIT_DEPLOYMENT") == "1":
        port = os.getenv("PORT")
        if port:
            try:
                return int(port)
            except ValueError:
                print(f"[Frontend] Invalid PORT value '{port}', falling back to {default_port}")
    return int(os.getenv("FRONTEND_PORT", default_port))

BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_PORT = get_frontend_port()

class ProxyHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        if self.path.startswith('/api/') or self.path == '/docs' or self.path == '/openapi.json' or self.path == '/redoc' or self.path == '/health':
            self.proxy_request('GET')
        else:
            parsed = urlparse(self.path)
            self.path = unquote(parsed.path)
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
    if process.stdout is not None:
        for line in process.stdout:
            print(f"[Backend] {line}", end='')
    return process

def run_frontend():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('0.0.0.0', FRONTEND_PORT), ProxyHandler)
    print(f"[Frontend] Serving on http://0.0.0.0:{FRONTEND_PORT}")
    server.serve_forever()

def init_database():
    """Initialize database tables on startup"""
    try:
        print("Initializing database...")
        env = os.environ.copy()
        result = subprocess.run(
            [sys.executable, 'backend/init_db.py'],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print(result.stdout)
        if result.returncode == 0:
            print("Database initialized successfully")
        else:
            if result.stderr:
                print(f"Database init errors: {result.stderr}")
    except Exception as e:
        print(f"Database initialization error (will retry on first request): {e}")

if __name__ == '__main__':
    init_database()
    
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    print("Waiting for backend to start...")
    time.sleep(3)
    
    run_frontend()
