# dashcam.py
# A Raspberry Pi powered, GPS enabled, 3D printed bicycle dashcam
# By Matthew Timmons-Brown, The Raspberry Pi Guy

import pygame
import picamera
import os
import sys
import io
import atexit
sys.path.insert(0, "/home/pi/bike_dashcam/libraries")
import yuv2rgb

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV'      , '/dev/fb1')
os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

size = width, height = 320, 240
rgb = bytearray(320 * 240 * 3)
yuv = bytearray(320 * 240 * 3 / 2)

pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

#screen = pygame.display.set_mode(size)
go_button = pygame.image.load("/home/pi/bike_dashcam/media/go.bmp")

camera = picamera.PiCamera()
atexit.register(camera.close)

sizeData = [ # Camera parameters for different size settings
 # Full res      Viewfinder  Crop window
 [(2592, 1944), (320, 240), (0.0   , 0.0   , 1.0   , 1.0   )], # Large
 [(1920, 1080), (320, 180), (0.1296, 0.2222, 0.7408, 0.5556)], # Med
 [(1440, 1080), (320, 240), (0.2222, 0.2222, 0.5556, 0.5556)]] # Small

sizeMode = 0

camera.resolution = sizeData[sizeMode][1]
camera.crop = (0.0,0.0,1.0,1.0)

while True:
        stream = io.BytesIO()
        camera.capture(stream, use_video_port=True, format='raw')
	stream.seek(0)
	stream.readinto(yuv)
	stream.close()

	yuv2rgb.convert(yuv, rgb, sizeData[sizeMode][1][0], sizeData[sizeMode][1][1])
	img = pygame.image.frombuffer(rgb[0:(sizeData[sizeMode][1][0] * sizeData[sizeMode][1][1] * 3)], sizeData[sizeMode][1], 'RGB')

#	yuv2rgb.convert(yuv, rgb, size[0], size[1])
#	img = pygame.image.frombuffer(rgb[0:(size[0]*size[1]*3)], size, 'RGB')
	screen.blit(img, ((320 - img.get_width() ) / 2, (240 - img.get_height()) / 2))
	pygame.display.update()
