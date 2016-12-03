#!/usr/bin/python
#
# Based on the Dlib example code:
#
# The contents of this file are in the public domain. See LICENSE_FOR_EXAMPLE_PROGRAMS.txt
#
#   This example program shows how to find frontal human faces in an image.  In
#   particular, it shows how you can take a list of images from the command
#   line and display each on the screen with red boxes overlaid on each human
#   face.
#
#   The examples/faces folder contains some jpg images of people.  You can run
#   this program on them and see the detections by executing the
#   following command:
#       ./face_detector.py ../examples/faces/*.jpg
#
#   This face detector is made using the now classic Histogram of Oriented
#   Gradients (HOG) feature combined with a linear classifier, an image
#   pyramid, and sliding window detection scheme.  This type of object detector
#   is fairly general and capable of detecting many types of semi-rigid objects
#   in addition to human faces.  Therefore, if you are interested in making
#   your own object detectors then read the train_object_detector.py example
#   program.  
#
#
# COMPILING THE DLIB PYTHON INTERFACE
#   Dlib comes with a compiled python interface for python 2.7 on MS Windows. If
#   you are using another python version or operating system then you need to
#   compile the dlib python interface before you can use this file.  To do this,
#   run compile_dlib_python_module.bat.  This should work on any operating
#   system so long as you have CMake and boost-python installed.
#   On Ubuntu, this can be done easily by running the command:
#       sudo apt-get install libboost-python-dev cmake
#
#   Also note that this example requires scikit-image which can be installed
#   via the command:
#       pip install -U scikit-image
#   Or downloaded from http://scikit-image.org/download.html. 


#serial.Serial('/dev/ttyACM1',9600,timeout=5)

from __future__ import division
import sys
from time import time, sleep
import threading
import serial #for motors

import cv2
import dlib
#from skimage import io


detector = dlib.get_frontal_face_detector()
try:
    win = dlib.image_window()
except:
    win = False
    
WAITMOVE = 0.2

import os
#Facepoint predictor
predictor = dlib.shape_predictor( os.path.expanduser('~/Downloads/shape_predictor_68_face_landmarks.dat') )

class webCamGrabber( threading.Thread ):
    def __init__( self ):
        threading.Thread.__init__( self )
        #Lock for when you can read/write self.image:
        #self.imageLock = threading.Lock()
        self.image = False
        
        from cv2 import VideoCapture, cv
        from time import time

        self.cam = VideoCapture(0)  #set the port of the camera as before
        #Doesn't seem to work:
        self.cam.set(cv.CV_CAP_PROP_FRAME_WIDTH, 160)
        self.cam.set(cv.CV_CAP_PROP_FRAME_WIDTH, 120)
        self.cam.set(cv.CV_CAP_PROP_FPS, 1)
        #self.cam.set(cv.CV_CAP_PROP_FPS, 1)
        
    def getImage( self ):
        #At .5 it finds face only within a few feet away. (2sec)
        return cv2.resize(self.image, (0,0), fx=0.6, fy=0.6)
        
    def run( self ):
        while True:
            start = time()
            #self.imageLock.acquire()
            retval, self.image = self.cam.read() #return a True bolean and and the image if all go right
            #print( "readimage: " + str( time() - start ) )
            #sleep(0.1)

if len( sys.argv[1:] ) == 0:

    #Start webcam reader thread:
    camThread = webCamGrabber()
    camThread.start()
    
    #Setup window for results
    detector = dlib.get_frontal_face_detector()
    #win = dlib.image_window()
    lastSmile = 0
    
    motors = serial.Serial('/dev/ttyACM0', 9600, timeout=5)
    
    while True:
        #camThread.imageLock.acquire()
        if camThread.image is not False:
            #print( "enter" )
            start = time()

            myimage = camThread.getImage()
            #for row in myimage:
            #    for px in row:
            #        #rgb expected... but the array is bgr?
            #        r = px[2]
            #        px[2] = px[0]
            #        px[0] = r
            
            
            dets = detector( myimage, 0)
            #print "your faces:" +str( len(dets) )
            nearFace = None
            nearFaceArea = 0
            
            for i, d in enumerate( dets ):
                #print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                #    i, d.left(), d.top(), d.right(), d.bottom()))
                screenArea = (d.right() - d.left()) * (d.bottom() - d.top())
                #print 'area', screenArea
                if screenArea > nearFaceArea:
                    nearFace = d
            #print( "face-find-time: " + str( time() - start ) )
            
            
            if nearFace != None: 
                b,g,r = cv2.split(myimage) #Because opencv has b,g,r not r,g,b
                start = time()
                if win:
                    win.clear_overlay()
                    win.set_image( cv2.merge( (r,g,b)) )
                    win.add_overlay(nearFace)
                #cv2.rectangle( myimage, (d.left(),d.top()), (d.right(), d.bottom()), (0,255,0), 1)
                #cv2.imshow('window', myimage)
                
                print( "show: " + str( time() - start ) )
                fromLeftFraction =  ( (nearFace.left() + nearFace.right()) / 2 ) / len(camThread.image[0])
                #print("from left: {}".format( fromLeftFraction ))
                #if fromLeftFraction < 0.25:
                #    motors.write('B')
                #    print( "LEFT" )
                #if fromLeftFraction > 0.75:
                #    motors.write('F')
                #    print( "RIGHT" )
                    
                print("from top: {}".format( ( (nearFace.top() + nearFace.bottom()) / 2 ) / len(camThread.image)) )
                
                points = (nearFace.left(), nearFace.top(), nearFace.right(), nearFace.bottom() )
                tracker = dlib.correlation_tracker()
                tracker.start_track( myimage, dlib.rectangle(*points))
                
                result = 11;
                while result > 10:
                    #Fix bgr->rgb:
                    b,g,r = cv2.split( camThread.getImage() )
                    myImage = cv2.merge((r,g,b))
                    result = tracker.update( myImage )
                    #print( 'result:')
                    #print( result )
                    rect = tracker.get_position()
                    start = time()
                    cx = (rect.right() + rect.left()) / 2
                    cy = (rect.top() + rect.bottom()) / 2
                    #print( 'correlationTracker %s,%s' % (cx, cy) )
                    #print rect has fractional.
                    if win:
                        win.clear_overlay()
                        win.set_image( myImage )
                        win.add_overlay( rect )
                    
                    fromLeft = ((rect.left() + rect.right())/2 ) / (len(myImage[0])) #width
                    #Move stepper:
                    if fromLeft >.9:
                        motors.write( 'B' )
                        sleep( WAITMOVE )
                    elif fromLeft >.75:
                        motors.write( 'b' )
                        sleep( WAITMOVE )
                    elif fromLeft <.1:
                        motors.write( 'F' )
                        sleep( WAITMOVE )
                    elif fromLeft <.25:
                        motors.write( 'f' )
                        sleep( WAITMOVE )
                    #Also highlight features?
                    #shape = predictor( myImage, nearFace )
                    #Integer to not error:
                    rect = dlib.rectangle( int(rect.left()), int(rect.top()), int(rect.right()), int(rect.bottom()) );
                    shape = predictor( myImage, rect )
                    #print("Part 0: {}, Part 1: {} ...".format(shape.part(0),
                    #                                          shape.part(1)))
                    # Draw the face landmarks on the screen.
                    #print "shape"
                    #print shape
                    #print dir(shape)
                    #while True:
                    #    print raw_input('>')
                    #for i in range(shape.num_parts):
                    #    print "%s:" % (i,)
                    #    pt = shape.part( i )
                    #    win.add_overlay( dlib.rectangle( pt.x, pt.y, pt.x+1, pt.y+1 ) )
                    #    raw_input();
                        #48-54 is top mouth
                        #To 60 (back left, below)
                    upLip = [shape.part(x) for x in range(48, 55)] #48 to 54
                    lowLip = [shape.part(n) for n in range(54, 61)] #54 to 60
                    #Make both left-to-right:
                    lowLip.reverse()
                    #print upLip
                    #print lowLip
                    if win:
                        for pt in upLip:
                            win.add_overlay( dlib.rectangle( pt.x, pt.y, pt.x+1, pt.y+1 ) )
                        for pt in lowLip:
                            win.add_overlay( dlib.rectangle( pt.x, pt.y, pt.x+1, pt.y+1 ) )
                    #Generate offsets relative to the leftmost mouth corner on picture:
                    upLipOffsets = [(part.x - upLip[0].x, part.y - upLip[0].y) for part in upLip]
                    lowLipOffsets = [(part.x - lowLip[0].x, part.y - lowLip[0].y) for part in lowLip]
                    #Those are now relative offsets from left, starting with (0,0) tuple.

                    #A simplified Proctustes evalutation - shear any rotation:
                    #Adjust second by 1/6, third by 2/6... until the last (7th after first) has 6/6 adjustment that will make it same level y as beginning.
                    upAdjust = -(upLipOffsets[6][1])
                    lowAdjust = -(lowLipOffsets[6][1])
                    #print upLipOffsets
                    #print( lowLipOffsets)
                    for i in range(7):
                        upLipOffsets[i] = (upLipOffsets[i][0], upLipOffsets[i][1] + i*upAdjust/6 )
                        lowLipOffsets[i] = (lowLipOffsets[i][0], lowLipOffsets[i][1] + i*lowAdjust/6 )
                    #print upLipOffsets
                    #print( lowLipOffsets)
                    #Divide by 5, last and first are adjusted to 0.
                    upAvg = sum([upLipOffsets[i][1] for i in range(7)]) / 5
                    lowAvg = sum([lowLipOffsets[i][1] for i in range(7)]) / 5
                    

                    #print( "Average down %d on upper lip, %d on lower lip" % ( upAvg, lowAvg ) )
                    
                    #raw_input()
                    if( upAvg + lowAvg > 5 ):
                        #Line average went down enough, \_/ smile.
                        print 'Smiled!'
                        if time() - 10 > lastSmile:
                            print 'Throttledsmile'
                            if motors:
                                motors.write( 'd' )
                            lastSmile = time()
                    #win.add_overlay(shape)
                    
                    #print( "show: " + str( time() - start ) )
                    #print( '%sx%s' % ( len(myImage) , len(myImage[0])) )
                    sleep( 0.001 )
                print( "Lost detection: %s" % (result,) )

            #dlib.hit_enter_to_continue()
    
    

#Unused:
for f in sys.argv[1:]:
    print("Processing file: {}".format(f))
    img = io.imread(f)
    # The 1 in the second argument indicates that we should upsample the image
    # 1 time.  This will make everything bigger and allow us to detect more
    # faces.
    dets = detector(img, 1)
    print("Number of faces detected: {}".format(len(dets)))
    for i, d in enumerate(dets):
        print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
            i, d.left(), d.top(), d.right(), d.bottom()))

    win.clear_overlay()
    win.set_image(img)
    win.add_overlay(dets)
    dlib.hit_enter_to_continue()


# Finally, if you really want to you can ask the detector to tell you the score
# for each detection.  The score is bigger for more confident detections.
# Also, the idx tells you which of the face sub-detectors matched.  This can be
# used to broadly identify faces in different orientations.
if (len(sys.argv[1:]) > 0):
    img = io.imread(sys.argv[1])
    dets, scores, idx = detector.run(img, 1)
    for i, d in enumerate(dets):
        print("Detection {}, score: {}, face_type:{}".format(
            d, scores[i], idx[i]))

