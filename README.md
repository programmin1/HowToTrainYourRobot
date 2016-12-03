# HowToTrainYourRobot
Easy-to-use, practical example of how to train Dlib to recognize objects.

HowToTrainYourRobotOverview.odt - One-page overview.

TheoryPoster.odt - OpenDocument format presentation.

Main.py - A graphical step by step trainer using Dlib and the webcam. Requires GTK+Python, fswebcam, and compiled IMGLAB and TRAINER binaries, compiled from the Dlib directory (Change path in the first lines).

Main.glade - An xml layout of the window, used by Main.py - Open it in Glade editor, which is a bit like WindowBuilder or Visual-Basic designer.

StepperShieldTest - Arduino motor shield controller - Turns one-letter commands through USB serial into motor movement.

faceDetectThreadCorrelationCV2FaceSmile.py - Computer software to connect to the Arduino - Assuming the plugged in usb shows up as /dev/ttyACM0, and you have webcam working, this should spin the candy dispenser when you smile at the camera.

Code examples based on Dlib.net examples under Boost software license.
