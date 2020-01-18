#!/usr/bin/env python
__author__ = "James Burnett"
__copyright__ = "Copyright (C) James Burnett (https://jamesburnett.io)"
__license__ = "GNU AGPLv3"
__maintainer__ = "James Burnett"
__email__ = "james@jamesburnett.io"
__status__ = "Development"

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import os
import io
import json
from PIL import Image

class Handler(BaseHTTPRequestHandler):
            
    def do_POST(self):

        if self.path == "/debug":

            message = "none"
            self.send_response(200)

            self.send_header("Content-Type","image/jpeg")
        
            self.end_headers()
            
            self.wfile.write(message)
        return


    def get_file(self,path):
        name, ext = os.path.splitext(self.path.split("?")[0])
        file = self.path.split("?")[0]
        if ext == ".css":
            return [file,"text/css",ext,name]
        elif ext == ".js":
            return [file,"application/javascript",ext,name]
        elif ext == ".html":
            return [file,"text/html",ext,name]
        elif ext == ".jpg":
            return [file,"image/jpeg",ext,name]
        elif ext == ".png":
            return [file,"image/png",ext,name]  
        elif ext == ".sjpg":
            return [file,"image/jpeg",ext,name]          
        elif ext == ".djpg":
            return [file,"image/jpeg",ext,name]          
        else:
            return [file,"text/plain",ext,name]
    

    def do_GET(self):

        
        ###Some useful variables
        ### self.requestpath - the full request path with GET/POST command
        ### self.path - Just the path requested (html file etc)
        ### self.command - The command. Is this a GET or POST etc?
        ### self.headers - A list of headers.
        
        
        
        
        http_file = self.get_file(self.path)
        
        cmd = self.path.split("/")

        #print("CMD" + cmd[1])

        message = None

        buffer = bytearray()

        try:
            doc = self.server.DocumentRoot + "/" + http_file[0]

            content_type = http_file[1]
            
            ext = http_file[2]

            if cmd[1] == "json":
                content_type = "text/html"
                #for stream in self.server.streams:
                #    self.server.data["streams"]
                message = str(json.dumps(self.server.data))
                buffer.extend(map(ord, message))
            elif cmd[1] == "frame":
                content_type = "image/jpeg"
                camno = int(cmd[2])
                frame = self.server.streams[camno].frameOrig
                if frame is not None:
                    img = Image.fromarray(frame)
                    img_io = io.BytesIO()
                    img.save(img_io, 'JPEG', quality=70)
                    img_io.seek(0)
                    message = img_io.read()           
                    buffer.extend(message)
                #print(cmd[2])

            elif ext == ".html" or ext == ".js" or ext == ".css":
                f=open(doc, "r")
                message = f.read()
                buffer.extend(map(ord, message))

            elif ext == ".png" or ext == ".jpg":
                f=open(doc, "rb")
                message = f.read()
                buffer.extend(message)

            elif ext == ".sjpg" or ext == ".djpg" :  #CAN REMOVE THIS AT SOME POINT WE NOW US /frame/0    /frame/1 etc to get image data from stream.
                stream_file = http_file[3].split("_")
                cam_number = int(stream_file[1])
                #print(stream_file[1])
                if ext == ".sjpg":
                    frame = self.server.streams[cam_number].frameOrig
                elif ext == ".djpg":
                    frame = self.server.streams[cam_number].frameDebug

                if frame is not None:
                    img = Image.fromarray(frame)
                    img_io = io.BytesIO()
                    img.save(img_io, 'JPEG', quality=70)
                    img_io.seek(0)
                    message = img_io.read()           
                    buffer.extend(message)
            else:
                x=1
                #print("Unknown or not found File: %s" % self.path)

                 
        except FileNotFoundError:
                message = "404 file not found." + doc
                print(message)
        except Exception as e:
                message = "Exception error reading html files." + str(e)
                print(message)

       
        try:
            self.send_response(200)
            self.send_header("Content-Type",content_type)
            self.end_headers()
            self.wfile.write(buffer)
        except BrokenPipeError:
            print("Broken Pipe")
        return
    def log_message(self, format, *args):
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    stream = None
    streams = []
    DocumentRoot = None
    time_start = 0
    data = {}
    data["stream_count"] = 0
    data["system_uptime"] = 0.0
    data["streams"] = []
    
    def init(self, DocumentRoot):
        self.thread_stopped = False
        self.DocumentRoot = DocumentRoot
       
    def serve_forever(self):
        while 1:
            if self.thread_stopped == True:
                break
            self.handle_request()

    def start_streams(self):
        self.data["stream_count"] = len(self.streams)
        for stream in self.streams:
            self.data["streams"].append(stream.data)
            stream.start()
        


    def setup(self):
        print("setup")

### for ssl
#httpd.socket = ssl.wrap_socket (httpd.socket, 
#        keyfile="path/to/key.pem", 
#        certfile='path/to/cert.pem', server_side=True)

    def stop(self):
        self.server_close()
        self.thread_stopped = True
        for stream in self.streams:
            stream.stop()

        print("Closing HTTP Sockets")
        self.server.socket.close()
        print("Stopping HTTP Server")
        self.server.server_close()
        exit()
