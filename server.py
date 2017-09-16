#!/usr/bin/env python3
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from urlparse import urlparse, parse_qs
import subprocess
import re
import os
import urllib
import requests
import json

memeUsername = ""
memePassword = ""

class S(BaseHTTPRequestHandler):
    def _set_headers(self, content):
        self.send_response(200)
        self.send_header('Content-type', content)
        self.end_headers()

    def checkLegacy(self, qs):
        # support old versions where ? was expected in beginning
        if qs[0] == "?":
            qs = qs.split("?")[1]
        return qs
    
    def qs_to_dict(self, qs):
        qs = self.checkLegacy(qs)
        final_dict = dict()
        for item in qs.split("&"):
            final_dict[item.split("=")[0]] = item.split("=")[1]
        return final_dict

    def makeMeme(self, id, top, bottom):
        #call imgflip and return the link
        try:
            global memeUsername
            global memePassword
            url     = 'https://api.imgflip.com/caption_image'
            payload = { 'template_id' : id,
                        'username' : memeUsername,
                        'password' : memePassword,
                        'text0' : top,
                        'text1' : bottom
                        }
            headers = {}
            res = requests.post(url, data=payload, headers=headers)
            data = json.loads(res.text)
            return data['data']['url']
        except Exception:
            return 'Could not create meme'

    def do_GET(self):
        path = os.path.abspath(__file__)
        fileName = scr_name = os.path.basename(__file__)
        path = path.replace(fileName, "")
        f = open(path + "index.html")
        self._set_headers('text/html')
        self.wfile.write(f.read())
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length) 
        parameters = self.qs_to_dict(post_data)

        try:
            scriptName = urllib.unquote(parameters["type"]).decode('utf8')
            scriptName = re.escape(scriptName)
            content = urllib.unquote(parameters["content"]).decode('utf8')
            content = re.escape(content)
        except Exception:
            self._set_headers('text/plain')
            self.wfile.write("Missing argument")
            return 

        if scriptName == 'spongebobmeme':
            url = self.makeMeme(103662437, '', content)
            self._set_headers('text/plain')
            self.wfile.write(url)
        
        elif scriptName == 'achievementmeme':
            try:
                title = urllib.unquote(parameters["title"]).decode('utf8')
                title = re.escape(title)
                url = self.makeMeme(3227693, title, content)
                self._set_headers('text/plain')
                self.wfile.write(url)
            except Exception:
                self._set_headers('text/plain')
                self.wfile.write("Missing title")

        elif (scriptName == 'revcalc') or (scriptName == 'pwdgen') or (scriptName == 'spellcheck'):
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
        
def run(server_class=HTTPServer, handler_class=S, port=80, username="", password=""):
    global memeUsername
    global memePassword
    memeUsername = username
    memePassword = password
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print ('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    elif len(argv) == 3:
        run(username=argv[2], password=argv[3])
    elif len(argv) == 4:
        run(port=int(argv[1]), username=argv[2], password=argv[3])
    else:
        run()