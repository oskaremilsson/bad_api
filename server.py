#!/usr/bin/env python3
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from urlparse import urlparse, parse_qs
import subprocess
import re
import os
import urllib

class S(BaseHTTPRequestHandler):
    def _set_headers(self, content):
        self.send_response(200)
        self.send_header('Content-type', content)
        self.end_headers()
    
    def qs_to_dict(self, qs):
        qs = qs.split("?")[1]
        final_dict = dict()
        for item in qs.split("&"):
            final_dict[item.split("=")[0]] = item.split("=")[1]
        return final_dict

    def do_GET(self):
        path = os.path.abspath(__file__)
        fileName = scr_name = os.path.basename(__file__)
        path = path.replace(fileName, "")
        f = open(path + "index.html")
        self._set_headers('text/html')
        self.wfile.write(f.read())
        
    def do_POST(self):
        # Doesn't do anything with posted data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length) 
        parameters = self.qs_to_dict(post_data)
        scriptName = parameters["type"]
        content = urllib.unquote(parameters["content"]).decode('utf8') 
        content = re.sub('\|(?!\|)' , '', content)
        content = re.escape(content)
        if (scriptName == 'revcalc') or (scriptName == 'pwdgen') or (scriptName == 'spellcheck'):
            self._set_headers('text/plain')
            self.wfile.write("Sorry, the api does not support this script")
        else :
            try:
                path = os.path.abspath(__file__)
                fileName = scr_name = os.path.basename(__file__)
                path = path.replace(fileName, "")
                proc = subprocess.Popen(["python3 %sbad_scripts/%s/%s.py %s" % (path, scriptName, scriptName, content)], stdout=subprocess.PIPE, shell=True)
                (output, err) = proc.communicate()

                self._set_headers('text/plain')
                self.wfile.write(output)
            except Exception:
                self._set_headers('text/plain')
                self.wfile.write("Error")
        
def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print ('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()