#!/usr/bin/env python
__author__ = "James Burnett"
__copyright__ = "Copyright (C) James Burnett (https://jamesburnett.io)"
__license__ = "GNU AGPLv3"
__maintainer__ = "James Burnett"
__email__ = "james@jamesburnett.io"
__status__ = "Development"

import os
import sys
import cv2
import time

sys.path.append('./lib/')
from video import VideoStream
from video import VideoPlayer
from config import Config
from httpd import ThreadedHTTPServer
from httpd import Handler

try:
    #defines specify the config file from the command line.
    config_file  = sys.argv[1]

except IndexError:
    print("usage: python ./ravenwatch.py /path/to/config.json")
    sys.exit();


#Get the directory that this program is running from
dirname, filename = os.path.split(os.path.abspath(__file__))

config = Config(config_file)

if config.isloaded == False:
    sys.exit(0)
    exit()


#The TCP port for this HTTP service to listen on.
HTTPPort = config.data["http_port"]

#The host or inteface IP to listen on.
HTTPHost = config.data["http_bind"]

#Sets the document root. Here we use the same folder that the http_server_thread.py is located.
DocumentRoot = dirname + "/htdocs"



if __name__ == '__main__':
    server = ThreadedHTTPServer((HTTPHost, HTTPPort), Handler)
    server.init(DocumentRoot)
    for source in config.data["sources"]:
        server.streams.append(VideoStream(source,config.data))
    
    server.start_streams()
    print("Starting HTTP Server")
    #print("Binding to port:%d" % config["http_port"])
    #print("Binding to address:%s" % config["http_bind"])
    print("Setting up DocumentRoot: %s" % DocumentRoot)
    print ('Server Started. Use <Ctrl-C> to stop')
    try:
        #debug_video = VideoPlayer(server.streams[0])

        #debug_video.start()

        server.serve_forever()
    except KeyboardInterrupt:
        print("Quiting via Ctl+C")
        

    #debug_video.stop()
        
    server.stop()

    sys.exit(0)
    exit()        
