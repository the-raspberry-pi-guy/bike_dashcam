# dashcam.py
# A Raspberry Pi powered, GPS enabled, 3D printed bicycle dashcam
# By Matthew Timmons-Brown, The Raspberry Pi Guy

import pygame
import picamera
import os
import sys
import io

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV'      , '/dev/fb1')
os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

size = width, height = 320, 240

pygame.init()
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode(size)
go_button = pygame.image.load("/home/pi/bike_dashcam/media/go.bmp")


