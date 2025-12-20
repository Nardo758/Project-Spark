import subprocess
import sys
import os
import signal
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.request import urlopen, Request, HTTPRedirectHandler, build_opener
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse, unquote
import threading
import json
from functools import partial


def get_static_root() -> str:
    """
    Static root for the frontend server.

    Prefer the built React app (frontend/dist). Fall back to repo root
    to preserve legacy static HTML during transition.
    """
    repo_root = os.path.dirname(os.path.abspath(__file__))
    react_dist = os.path.join(repo_root, "frontend", "dist")
    if os.path.isdir(react_dist):
        return react_dist
    return repo_root


class NoRedirectHandler(HTTPRedirectHandler):
    """Custom handler that doesn't follow redirects - returns them instead"""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Don't follow redirects

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

# Global flag to track backend readiness
backend_ready = False

def wait_for_backend(timeout=60):
    """Wait for backend to be ready by checking health endpoint"""
    global backend_ready
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            req = Request(f'http://localhost:{BACKEND_PORT}/health', method='GET')
            with urlopen(req, timeout=5) as response:
                if response.status == 200:
                    backend_ready = True
                    print(f"[Server] Backend is ready after {time.time() - start_time:.1f}s")
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    
    print(f"[Server] Warning: Backend not responding after {timeout}s, continuing anyway...")
    backend_ready = True  # Allow requests to proceed, they'll get proper errors
    return False

class ProxyHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        # Backend routes to proxy (be specific to avoid intercepting frontend routes like /auth/magic)
        backend_auth_routes = ['/auth/login', '/auth/callback', '/auth/logout', '/auth/status', '/auth/debug']
        is_backend_auth = any(self.path.startswith(route) for route in backend_auth_routes)
        if self.path.startswith('/api/') or is_backend_auth or self.path.startswith('/__repl_auth') or self.path == '/docs' or self.path == '/openapi.json' or self.path == '/redoc' or self.path == '/health':
            self.proxy_request('GET')
        else:
            parsed = urlparse(self.path)
            self.path = unquote(parsed.path)

            # SPA fallback: if the requested path isn't a real file, serve index.html
            # so React Router can handle client-side routes (e.g., /validations).
            try:
                local_path = self.translate_path(self.path)
                basename = os.path.basename(local_path)
                has_extension = '.' in basename
                if (not has_extension) and (not os.path.exists(local_path)):
                    self.path = '/index.html'
            except Exception:
                # If path translation fails, fall back to default behavior.
                pass

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
        global backend_ready
        backend_url = f'http://localhost:{BACKEND_PORT}{self.path}'
        
        # If backend not ready yet, wait a bit
        if not backend_ready:
            retries = 10
            while not backend_ready and retries > 0:
                time.sleep(0.5)
                retries -= 1
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            headers = {}
            for header in ['Content-Type', 'Authorization', 'Accept', 'Cookie']:
                if self.headers.get(header):
                    headers[header] = self.headers.get(header)
            
            req = Request(backend_url, data=body, headers=headers, method=method)
            
            # Use opener that doesn't follow redirects
            opener = build_opener(NoRedirectHandler)
            
            try:
                response = opener.open(req, timeout=30)
                self.send_response(response.status)
                for header, value in response.headers.items():
                    if header.lower() not in ['transfer-encoding', 'connection']:
                        self.send_header(header, value)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.read())
            except HTTPError as e:
                # HTTPError is raised for redirects (3xx) and client/server errors (4xx, 5xx)
                if e.code in (301, 302, 303, 307, 308):
                    # Pass redirect back to client
                    self.send_response(e.code)
                    for header, value in e.headers.items():
                        if header.lower() not in ['transfer-encoding', 'connection']:
                            self.send_header(header, value)
                    self.end_headers()
                else:
                    # Regular HTTP error
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
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'detail': 'Backend unavailable. Please try again in a moment.'}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
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
    static_root = get_static_root()
    handler = partial(ProxyHandler, directory=static_root)
    server = HTTPServer(('0.0.0.0', FRONTEND_PORT), handler)
    print(f"[Frontend] Serving static files from: {static_root}")
    print(f"[Frontend] Serving on http://0.0.0.0:{FRONTEND_PORT}")
    server.serve_forever()

def init_database():
    """
    Apply database migrations on startup.

    Notes:
    - Deployments should always apply migrations.
    - Seeding demo data is optional and controlled via SEED_DB=1.
    """
    repo_root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(repo_root, "backend")
    env = os.environ.copy()

    try:
        print("[DB] Applying migrations (alembic upgrade head)...")
        env["PYTHONPATH"] = backend_dir
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
            cwd=backend_dir,
        )
        if result.stdout:
            print(result.stdout)
        if result.returncode == 0:
            print("[DB] Migrations applied successfully")
        else:
            if result.stderr:
                print(f"[DB] Migration errors: {result.stderr}")
            print("[DB] Warning: migrations failed (app may be inconsistent).")
    except Exception as e:
        print(f"[DB] Migration error (app may be inconsistent): {e}")

    if os.getenv("SEED_DB") == "1":
        try:
            print("[DB] SEED_DB=1 set; running backend/init_db.py (demo seed)...")
            seed_result = subprocess.run(
                [sys.executable, "init_db.py"],
                capture_output=True,
                text=True,
                timeout=180,
                env=env,
                cwd=backend_dir,
            )
            if seed_result.stdout:
                print(seed_result.stdout)
            if seed_result.returncode != 0 and seed_result.stderr:
                print(f"[DB] Seed errors: {seed_result.stderr}")
        except Exception as e:
            print(f"[DB] Seed error: {e}")

if __name__ == '__main__':
    init_database()
    
    # Start backend in a thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    print("Waiting for backend to start...")
    
    # Wait for backend to be ready in a separate thread so frontend can start
    def wait_and_mark_ready():
        wait_for_backend(timeout=30)
    
    wait_thread = threading.Thread(target=wait_and_mark_ready, daemon=True)
    wait_thread.start()
    
    # Give backend a few seconds head start
    time.sleep(5)
    
    run_frontend()
