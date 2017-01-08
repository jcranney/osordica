#!/usr/bin/env python

from scipy.io import wavfile
import argparse
import numpy as np
import pygame
import sys
import warnings
#import RPi.GPIO as GPIO

# need 10 digitals to be used as keys:
# L0 is left pinky, R4 is right thumb etc
#
#   Finger |  Pin  | GPIOnum
#     L0   |   11  |   17
#     L1   |   13  |   27
#     L2   |   15  |   22
#     L3   |   12  |   18 
#     L4   |   16  |   23
#     R0   |   29  |    5
#     R1   |   31  |    6
#     R2   |   33  |   13 
#     R3   |   32  |   12 
#     R4   |   37  |   26 
#
# 1 digital to be used as strum:
#
#	Strum  |   7   |    4  
#

class Button:
	"""Button variable class for keyboard buttons"""
	pressed = 0
	def __init__(self,finger,pin,GPIOnum):
		self.finger = finger
		self.pin = pin
		self.GPIOnum = GPIOnum

pins = [11, 13 ,15, 12, 16, 29, 31, 33, 32, 37]
GPIOnums = [17, 27, 22, 18, 23, 5, 6, 13, 12, 26]
finger_names = ["L0", "L1", "L2", "L3", "L4", "R0", "R1", "R2", "R3", "R4"]
fingers = [Button(finger_names[x],pins[x],GPIOnums[x]) for x in range(10)]


#need to map raspberrypi io's

#need to load audio sample file

#need to generate clean sine waves of required frequencies to see if it sounds better

#need to stretch and attenuate/amplify scaled sound

#need to do lots of other stuff, if you think of anything just add it
