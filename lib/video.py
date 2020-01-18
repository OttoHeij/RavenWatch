#!/usr/bin/env python
__author__ = "James Burnett"
__copyright__ = "Copyright (C) James Burnett (https://jamesburnett.io)"
__license__ = "GNU AGPLv3"
__maintainer__ = "James Burnett"
__email__ = "james@jamesburnett.io"
__status__ = "Development"

from threading import Thread
import cv2
import datetime
import time
import numpy as np 

from PIL import Image
from detection import MotionDetection
from detection import HumanDetection
from alerts import Email


class VideoStream(MotionDetection,HumanDetection):

    def __init__(self,source,config):
        print("Starting stream %s" % source["name"])
        #noimg_pil = Image.open('./noimage.jpg')
        #self.noimg_frame = np.array(noimg_pil.getdata())
        self.noimg_frame = cv2.imread('noimage.jpg',0)
        self.source = source
        self.config = config
        self.frame = None
        self.frameOrig = None
        self.thread_stopped = False
        self.frame_counter = 0
        self.status = self.source["name"] + "|starting stream|" 
        self.config = config
        
        self.data = {}
        self.data["uptime"] = 0
        self.data["stream_name"] = self.source["name"]
        self.data["stream_uri"] = self.source["uri"]

        #self.email = Email(config.data["email_server"],config.data["email_server_username"],config.data["email_server_password"])
        
        MotionDetection.__init__(self,self.source["fps"])
        HumanDetection.__init__(self)
        
        print("%s Initialized." % self.source["name"])


    def start(self):
        Thread(target=self.update, args=()).start()
        return self


    def reconnect(self):
        self.status = self.source["name"] + "|Problem Reading Frames"
        print("Reconnecting %s" % self.source["name"])
        self.rtsp = cv2.VideoCapture(self.source["uri"])
        time.sleep(2.00)


    def get_frame(self,frame):
        now = datetime.datetime.now()
        strdate = str(now.month) + "-" + str(now.day) + "-" + str(now.year)
        strtime = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)

        new_frame = frame.copy()

        font                   = cv2.FONT_HERSHEY_SIMPLEX
        fontScale              = 0.50
        lineType               = 1
        cv2.rectangle(new_frame,(0,0),(640,24), (0,0,0), -1)
        cv2.putText(new_frame,str(self.source["name"]), (10,16), font, 0.75,(255,2255,255),2)
        v = "{0:.2f}".format(self.frame_penetration_pct)
        cv2.putText(new_frame,"M:" + v, (110,14), font, fontScale,(255,2255,255),lineType)
        cv2.putText(new_frame,str(strdate), (210,14), font, fontScale,(255,255,255),lineType)
        cv2.putText(new_frame,str(strtime), (340,14), font, fontScale,(255,255,255),lineType)
        return new_frame


    def update(self):

        
        while self.source["offline"] == 1:
            self.data["uptime"] = self.data["uptime"] + 1
            self.frameOrig = self.get_frame(self.noimg_frame)
            #print(self.data["uptime"])
            time.sleep(1)
        

        self.rtsp = cv2.VideoCapture(self.source["uri"])

        score_data = []

        motion_started = False

        pre_buffer = []

        write_buffer = []

        time_start = 0.0

        time_diff = 0.0;

        frame_errors = 0


        frame_motion_counter = 0

        while True:
            #self.data["uptime"] = self.data["uptime"] + 1

            if self.thread_stopped == True:
                break

            if self.rtsp.isOpened() is False:
                self.reconnect()
                continue


            ret, f = self.rtsp.read()

            if ret is False:
                if frame_errors >= 10:
                    self.rtsp.release()
                frame_errors = frame_errors + 1
                self.status = self.source["name"] + "|Problem Reading Frames|" + str(frame_errors)
                print("Problem reading frames: %d" % frame_errors)
                time.sleep(2)
                continue

            self.frameOrig = self.get_frame(f)

            self.frame = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)



            #####use this to throttle frame. Do not use for motion detection calculate_motion_scores###
            #if self.frame_counter < 30:
            #    self.frame_counter = self.frame_counter + 1
            #    continue
            #else:
            #    self.frame_counter = 0
            

            

            #self.calculate_motion_scores(self.frame)
            
            #self.calculate_human_detection(self.frame)

                  
            
            ########keep frames for pre-event recording###########
            if len(pre_buffer) == 400:
                del pre_buffer[0]

            if len(pre_buffer) < 400:
                pre_buffer.append(self.frameOrig)
                
            
            if self.motion_score_avg > 14 and motion_started is False:
                del write_buffer[:]
                time_diff = 0.0
                time_start = time.time()
                #print("Motion Started %d" % time_start)
                write_buffer = pre_buffer
                #motion_started = True   UNCOMMENT TO PLAY WITH MOTION DETECTION
            
            ticks = time.time()

            if motion_started is True:
                print("Motion Started")
                #start capturing still images for email alert?
                temp_file = "/tmp/frame-" + str(frame_motion_counter) + ".jpg"
                resized = cv2.resize(self.frameOrig, None, fx=0.5, fy=0.5, interpolation = cv2.INTER_LINEAR)
                cv2.imwrite(temp_file,resized,[int(cv2.IMWRITE_JPEG_QUALITY), 87])
                
                if frame_motion_counter%4 == 0:
                    #self.email.add_attachment(temp_file)
                    print("Divible by 4")
                    
                frame_motion_counter = (frame_motion_counter + 1)
                    
                if self.motion_score_avg < 10:
                    time_diff = ticks - time_start
                    #print(time_diff)
                else:
                     time_start = time.time()

                write_buffer.append(self.frameOrig)

                if time_diff >= 5.00 and self.motion_score_avg < 10.00:
                    motion_started = False
                    #if self.config.data["send_alerts"] is "yes":
                    #    self.email.send_email("james@burnett.tech","james@burnett.tech","Motion Alert","Motion was detect on a camera.")
                    #self.email.clear_attachments()
                    now = datetime.datetime.now()

                    #outfile = "/home/james/Nextcloud/Motion/" + self.camname + "-" + str(now.hour) + "-" + str(now.minute) + "-" + str(now.second)+ ".avi"
                    #fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    height, width = self.frame.shape
                    #print("Writing %d x %d" % (width,height))
                    out = cv2.VideoWriter(outfile, fourcc, 20.0, (width,height),True)
                    ct = 0
                    for f in write_buffer:
                        ct = ct + 1
                        #out.write(f)                      #DONT FORGET TO UNCOMMENT FOR WRITING OUTPUT
                    out.release()
                    #print(ct)
        print("Video Thread Existing Worker")
        
    def read(self):
        return self.frame

    def stop(self):
        print("Stopping Video Thread")
        self.thread_stopped = True
        exit()


class VideoPlayer():
        def __init__(self,video_stream):
            self.video_stream = video_stream
            self.thread_stopped = False
            self.debug = False

        def start(self):
            self.video_stream.start()
            Thread(target=self.update, args=()).start()
            return self

        def update(self):
            while True:
                if self.thread_stopped == True:
                    break

                if self.video_stream.frame is not None:
                    try:
                        if self.debug == False:
                            cv2.imshow("Main Frame", self.video_stream.frame)
                        else:
                            cv2.imshow("Debug Frame", self.video_stream.frameDebug)
                    except:
                        print("VideoPlayer Error")
                    key = cv2.waitKey(1) & 0xFF
                    
                    #time.sleep(0.225)
                    

        def stop(self):
            self.thread_stopped = True
            exit()
