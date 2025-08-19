from http.server import HTTPServer, SimpleHTTPRequestHandler

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        return super().end_headers()

PORT = 8000

httpd = HTTPServer(("0.0.0.0", PORT), CORSRequestHandler)
print(f"Serving with CORS on http://localhost:{PORT}")
httpd.serve_forever()
