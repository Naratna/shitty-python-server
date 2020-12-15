from typing import Pattern
from urllib import parse
import http.server 
import socketserver
import os
import subprocess
import argparse

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url = parse.urlsplit(self.path)
        if os.path.splitext(url.path)[1] == ".py":
            path = parse.unquote_plus(url.path)
            path = os.path.abspath(os.path.join(".", path[1:]))
            self._execute_command(path, url.query)
        else:
            super().do_GET()
    
    def _execute_command(self, path: str, query: str):
        self.protocol_version = "HTTP/1.1"
        print(f"Path: {path}" )
        print(f"Query: {query}")
        if not os.path.isfile(path):
            self.respond("The specified script could not be found", 404, "text/plain")
            return
        try:
            process = subprocess.run(["python", path, query], stdout=subprocess.PIPE)
        except Exception as ex:
            self.respond("An error ocurred while processing your request", 500, "text/plain")
            print("Error:", ex)
        else:
            if process.returncode != 69:
                self.respond('{"Error":"An error ocurred"}')
            elif process.stdout is not None:
                response = process.stdout.decode("utf-8")
                self.respond(response)
                print("UwU")
            else:
                self.respond('{"Success":"The command was succesful"}')

    def respond(self, message: str, code: int = 200, content_type = "application/json"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(message))
        self.end_headers()
        self.wfile.write(bytes(message, "utf-8"))

def main():
    handler = RequestHandler

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=80, dest="port", help="The port for the server")
    parser.add_argument("-d", "--directory", type=str, default=".", dest="dir", help="The root directory for the server")

    args = parser.parse_args()

    os.chdir(args.dir)

    with socketserver.TCPServer(("", args.port), handler) as httpd: 
        print("serving at port", args.port) 
        httpd.serve_forever()
    
if __name__ == "__main__":
    main()