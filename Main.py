#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0") # Do not try GTK4 if available, Glade file is GTK3
from gi.repository import Gtk, GdkPixbuf, Gdk
import urllib
import os
import datetime
import time
import shutil
import subprocess
import dlib
from time import sleep
from skimage import io

#IMGLAB compiled binary:
IMGLAB = '~/Progs/dlib-19.24/tools/imglab/build/imglab'
#Trainer example compiled binary:
TRAINER = '~/Progs/dlib-18.16/examples/build/fhog_object_detector_ex'

class ExplainerWin():
	def __init__(self):
		self.builder = Gtk.Builder()
		self.builder.add_from_file("Main.glade")
		self.builder.connect_signals({
			'btn1' : self.step1,
			'btn2' : self.step2,
			'btn3' : self.step3,
			'btn4' : self.step4,
			'btn5' : self.step5
		})
		self.window = self.builder.get_object("window1")
		self.window.connect("destroy", Gtk.main_quit)
		self.imgnum = 0
		#Adjust as necessary:
		camera = 'usb-Microsoft_Microsoft®_LifeCam_VX-2000-video'
		if os.environ.get('WEBCAM'):
			camera = os.environ.get('WEBCAM')
		self.extraparam = '--device /dev/v4l/by-id/'+camera+'-index0'
		
		self.tmp = "/tmp/train"+datetime.datetime.strftime(datetime.datetime.now(), '%H-%M-%S')
		os.mkdir( self.tmp )
		print( self.tmp )
		css = b""".large {
    color: blue;
    font-weight: bolder;
    font-size:32px;
    border-style: solid;
    border-width: 2px 0 2px 2px;
    padding: 8px;
}"""
		style_provider = Gtk.CssProvider()
		style_provider.load_from_data(css)

		Gtk.StyleContext.add_provider_for_screen(
			Gdk.Screen.get_default(),
			style_provider,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
		self.builder.get_object("button1").set_alignment(0,0);
		self.builder.get_object("button2").set_alignment(0,0);
		self.builder.get_object("button3").set_alignment(0,0);
		self.builder.get_object("button4").set_alignment(0,0);
		self.builder.get_object("button5").set_alignment(0,0);
	
	def step1(self, btn):
		self.imgnum += 1
		#TODO direct read with opencv2 and show on this window?
		#cam = cv2.VideoCapture(0)
		#ret, frame = cam.read()
		#imagecontrol = self.builder.get_object("image")
		os.system( 'fswebcam %s %s/img%s.jpg' % (self.extraparam, self.tmp, self.imgnum) )
		if os.system( 'xdg-open %s/img%s.jpg' % (self.tmp, self.imgnum) ):
			#nonzero exit
			print("Use env variable, WEBCAM=nameofcam if it exists as /dev/v4l/by-id/nameofcam-index0")
		
	def step2(self, btn):
		os.system( IMGLAB + ' -c %s/training.xml %s'  % (self.tmp, self.tmp) )
		
	def step3(self, btn):
		os.system( IMGLAB + ' %s/training.xml' % (self.tmp,) )
			
	def step4(self, btn):
		#Based on dlib example:
		# Now let's do the training.  The train_simple_object_detector() function has a
		# bunch of options, all of which come with reasonable default values.  The next
		# few lines goes over some of these options.
		
		options = dlib.simple_object_detector_training_options()
		
		# Since faces are left/right symmetric we can tell the trainer to train a
		# symmetric detector.  This helps it get the most value out of the training
		# data.
		
		options.add_left_right_image_flips = True
		
		# The trainer is a kind of support vector machine and therefore has the usual
		# SVM C parameter.  In general, a bigger C encourages it to fit the training
		# data better but might lead to overfitting.  You must find the best C value
		# empirically by checking how well the trained detector works on a test set of
		# images you haven't trained on.  Don't just leave the value set at 5.  Try a
		# few different C values and see what works best for your data.
		
		options.C = 5
		
		# Tell the code how many CPU cores your computer has for the fastest training.
		options.num_threads = 4
		options.be_verbose = True
		
		trainingXML =  os.path.join(self.tmp, 'training.xml')
		#Ideally there would be half training, half testing:
		testingXML = os.path.join(self.tmp, "training.xml")
		
		# This function does the actual training.  It will save the final detector to
		# detector.svm.  The input is an XML file that lists the images in the training
		# dataset and also contains the positions of the face boxes.  To create your
		# own XML files you can use the imglab tool which can be found in the
		# tools/imglab folder.  It is a simple graphical tool for labeling objects in
		# images with boxes.
		dlib.train_simple_object_detector(trainingXML, os.path.join( self.tmp, "detector.svm"), options)
		print("Training accuracy: {}".format(
			dlib.test_simple_object_detector(trainingXML, os.path.join( self.tmp, "detector.svm") )))
		
	def step5(self, btn):
		#Take photo
		self.imgnum += 1
		os.system( 'fswebcam %s %s/img%s.jpg' % (self.extraparam, self.tmp, self.imgnum) )
		
		detector = dlib.simple_object_detector( os.path.join( self.tmp, "detector.svm" ) )
		win = dlib.image_window()
		
		start = time.time()
		img = io.imread( '%s/img%s.jpg' % (self.tmp, self.imgnum))
		# The 1 in the second argument indicates that we should upsample the image
		# 1 time.  This will make everything bigger and allow us to detect more
		# faces.
		dets = detector(img, 1)
		print("detected: {}".format(len(dets)))
		for i, d in enumerate(dets):
			print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
				i, d.left(), d.top(), d.right(), d.bottom()))
		
		print ("took " + str(time.time() - start) )
		win.clear_overlay()
		win.set_image(img)
		win.add_overlay(dets)
		sleep(2)


		

if __name__ == '__main__':
	explainer = ExplainerWin()
	explainer.window.show_all()
	Gtk.main()

