#!/usr/bin/env python3
"""
🚀 OppGrid Test Server - Works without external dependencies
For testing frontend connectivity and basic functionality
"""

import http.server
import socketserver
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>OppGrid Test Server</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
                    .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                    .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
                    .endpoint { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; font-family: monospace; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 OppGrid Test Server</h1>
                    <div class="status success">✅ Server is running successfully!</div>
                    <div class="status info">🎯 Frontend can connect to this test server</div>
                    
                    <h3>Available Test Endpoints:</h3>
                    <div class="endpoint">GET /api/test - Basic connectivity test</div>
                    <div class="endpoint">GET /api/opportunities - Sample opportunities data</div>
                    <div class="endpoint">GET /api/health - Health check</div>
                    <div class="endpoint">GET /api/agents - Sample agents data</div>
                    
                    <h3>Test Frontend Connection:</h3>
                    <p>Open your browser console and run:</p>
                    <pre>fetch('http://localhost:8000/api/test').then(r => r.json()).then(console.log)</pre>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            
        elif path == '/api/test':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "success",
                "message": "OppGrid test server responding",
                "timestamp": time.time(),
                "server": "Test Server v1.0"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "services": {
                    "api": "running",
                    "database": "test_mode",
                    "ai_services": "simulated"
                },
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/opportunities':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "opportunities": [
                    {
                        "id": 1,
                        "title": "AI-Powered Market Research Tool",
                        "description": "Automated competitor analysis for small businesses",
                        "category": "Technology",
                        "feasibility_score": 85,
                        "validation_count": 23,
                        "created_at": "2026-01-15T10:30:00Z"
                    },
                    {
                        "id": 2,
                        "title": "Local Service Marketplace",
                        "description": "Connect local service providers with customers",
                        "category": "Local Business",
                        "feasibility_score": 78,
                        "validation_count": 15,
                        "created_at": "2026-01-14T14:20:00Z"
                    }
                ],
                "total": 2,
                "page": 1,
                "per_page": 10
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/agents':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "agents": [
                    {
                        "id": "market-research-pro",
                        "name": "Market Research Pro",
                        "status": "active",
                        "capabilities": ["opportunity_analysis", "market_research"],
                        "usage": {"calls": 847, "success_rate": 94.2},
                        "cost_per_analysis": 5.0
                    },
                    {
                        "id": "idea-validator",
                        "name": "Idea Validator", 
                        "status": "active",
                        "capabilities": ["feasibility_analysis", "validation"],
                        "usage": {"calls": 1234, "success_rate": 89.7},
                        "cost_per_analysis": 0.0
                    }
                ]
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Endpoint not found", "path": path}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        if self.path == '/api/test':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "received",
                "method": "POST",
                "data_received": post_data.decode('utf-8')[:100],
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.do_GET()  # Fallback to GET handler
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server():
    """Run the test server"""
    port = 8000
    handler = TestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 OppGrid Test Server running on port {port}")
        print(f"📊 Access at: http://localhost:{port}")
        print("🔍 API endpoints:")
        print(f"   • http://localhost:{port}/api/test")
        print(f"   • http://localhost:{port}/api/health")
        print(f"   • http://localhost:{port}/api/opportunities")
        print(f"   • http://localhost:{port}/api/agents")
        print("\\n🛑 Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\n🛑 Server stopped")

if __name__ == "__main__":
    run_server()