#!/usr/bin/env python
__author__ = "James Burnett"
__copyright__ = "Copyright (C) James Burnett (https://jamesburnett.io)"
__license__ = "GNU AGPLv3"
__maintainer__ = "James Burnett"
__email__ = "james@jamesburnett.io"
__status__ = "Development"

import cv2
import imutils
import numpy




class HumanDetection:
    
    def __init__(self):
        self.enable_human_detection = True
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.human_detection_weight = 0.0
        
    def calculate_human_detection(self,frame):
        frame = cv2.resize(frame,(320,240))

        tframe = frame.copy()

        rects, weights = self.hog.detectMultiScale(tframe,winStride=(20,20),padding=(16,16), scale=1.01, useMeanshiftGrouping=False)
                
        for i, (x, y, w, h) in enumerate(rects):
            #cv2.rectangle(self.framePeople, (x,y), (x+w,y+h),(0,255,0),2)
            self.human_detection_weight = weights[i][0]
             



class MotionDetection:

    def __init__(self,fps):
        self.motion_score = 0.0
        self.motion_score_avg = 0.0
        self.motion_distance = 0.0
        self.frame_buffer = []
        self.score_data = []
        self.fps = fps
        self.frameDelta = None
        self.frameDebug = None
        self.disable_motion_detection = False
        self.frame_penetration_pct = 0.0


    def calculate_object_pct(self, frame):
        no_wht = 0
        #for i in range (frame.shape[0]): #traverses through height of the image
        #    for j in range (frame.shape[1]): #traverses through width of the image
        #        val = frame[i][j] 
        #        if val > 10 :
        #            no_wht = no_wht + 1 
        framex = numpy.ma.masked_less_equal(frame, 40)
        no_wht = numpy.average(framex)
        #if no_wht > 5:
        #    print(no_wht)
        #tot_pixel = frame.size
        #percentage = 0.0 # round(no_wht * 100 / tot_pixel, 2)
        return no_wht 

    def calculate_motion_scores(self,frame):
        if self.disable_motion_detection == True:
            return
        
        reframe = cv2.resize(frame,(640,480))

        #reframe = frame.copy()

        if self.frameDelta is None:
            self.frameDelta = reframe

        if len(self.frame_buffer) == self.fps:
            self.frame_buffer.pop()
            self.frame_buffer.insert(0,reframe)
        else:
            self.frame_buffer.append(reframe)

     
        self.frameDelta = cv2.absdiff(self.frame_buffer[0],self.frame_buffer[len(self.frame_buffer) - 1])

        self.frameDelta = cv2.GaussianBlur(self.frameDelta, (5, 5), 0)

        thresh = cv2.threshold(self.frameDelta, 50, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.erode(thresh, None, iterations=2)

        thresh = cv2.dilate(thresh, None, iterations=2)

        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        cnts = imutils.grab_contours(cnts)

        self.frame_penetration_pct = self.calculate_object_pct(self.frameDelta) 

        if cnts is not None:
            if len(cnts) > 0:
                img = self.frameDelta.copy()
                c = max(cnts, key=cv2.contourArea)
                extLeft = tuple(c[c[:, :, 0].argmin()][0])
                extRight = tuple(c[c[:, :, 0].argmax()][0])
                extTop = tuple(c[c[:, :, 1].argmin()][0])
                extBot = tuple(c[c[:, :, 1].argmax()][0])

                cv2.circle(img, extLeft, 8, (255, 255, 255), -1)
                cv2.circle(img, extRight, 8, (155, 155, 155), -1)
                self.motion_distance = extRight[0] - extLeft[0]
                
                #if self.motion_distance > 40:
                #    print(self.motion_distance)
                self.frameDebug = img
            else:
                self.motion_distance = 0                
                self.frameDebug = self.frameDelta
                    

            self.motion_score  = len(cnts)

            if len(self.score_data) < 21:
                self.score_data.append(self.motion_score)
            else:
                self.score_data.pop()
                self.score_data.insert(0,self.motion_score)
        else:
                self.frameDebug = self.frameDelta
        
        self.motion_score_avg = round((sum(self.score_data) / len(self.score_data)),3)

