from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Status : Online")
        else:
            self.send_response(404)
            self.end_headers()

def run():
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()

def keep_alive():
    t = Thread(target=run)
    t.start()

# Start the server
keep_alive()
