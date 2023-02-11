import socketserver
from http.server import BaseHTTPRequestHandler
import os
from dotenv import load_dotenv

load_dotenv()
def some_function():
    print("some_function got called")

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        return

print()
server_infos: tuple[str, int] = (os.getenv("URL_HEALTH_CHECK"), int(os.getenv("PORT_HEALTH_CHECK")))
print("server_infos :", server_infos)
httpd: socketserver.TCPServer = socketserver.TCPServer(server_address=server_infos, RequestHandlerClass=MyHandler)


def start_health_check():
    httpd.serve_forever()

def stop_health_check():
    httpd.shutdown()