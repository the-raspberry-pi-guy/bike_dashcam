# dashcam.py
# A Raspberry Pi powered, GPS enabled, 3D printed bicycle dashcam
# By Matthew Timmons-Brown, The Raspberry Pi Guy

# Import necessary modules
import pygame
import picamera
import fnmatch
import os
import sys
import io
import atexit
import time
import threading
import subprocess
# Change path and import Adafruit's yuv2rgb library
sys.path.insert(0, "/home/pi/bike_dashcam/libraries")
import yuv2rgb

# Change screen to PiTFT, init framebuffer/touchscreen environment variables
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV'      , '/dev/fb1')
os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

# Set size of display and create buffers for display data
size = width, height = 320, 240
rgb = bytearray(320 * 240 * 3)
yuv = bytearray(320 * 240 * 3 / 2)

# Startup and setup Pygame and screen
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

# Startup and setup the Raspberry Pi official camera
#camera = picamera.PiCamera()
#atexit.register(camera.close)
#camera.resolution = size
#camera.crop = (0.0,0.0,1.0,1.0)

class Icon:
	"""A simple icon bitmap class that connects a name to a pygame image"""
	
	def __init__(self, name):
		self.name = name
		try:
			self.bitmap = pygame.image.load("/home/pi/bike_dashcam/media/" + name + ".png")
		except:
			pass

class Button:
	"""A button class to control all aspects of touchscreen buttons"""
	def __init__(self, rect, **kwargs):
		self.rect = rect
		self.icon_name = None
		self.icon = None
		self.callback = None
		self.value = None
		# All of the properties a button can have
		# Name, linked icon file, its own callback function etc
		for key, value in kwargs.iteritems():
			if key == "icon": self.icon = value
			elif key == "icon_name": self.icon_name = value
			elif key == "callback": self.callback = value
			elif key == "value": self.value = value

	# Function to check whether or not a button has been pressed
	# If pressed, trigger that button's callback function, if it has one
	def selected(self, pos):
		x1 = self.rect[0]
		y1 = self.rect[1]
		x2 = x1 + self.rect[2] - 1
		y2 = y1 + self.rect[3] - 1
		if ((pos[0] >= x1) and (pos[0] <= x2) and (pos[1] >= y1) and (pos[1] <= y2)):
			print "Touch registered"
			if self.callback:		
				if self.value is None:
					self.callback()
				else:
					self.callback(self.value)
			return True
		return False

	# Function to draw a button onto the screen
	def draw(self, screen):
		if self.icon:
			screen.blit(self.icon.bitmap,(self.rect[0]+(self.rect[2]-self.icon.bitmap.get_width())/2, self.rect[1]+(self.rect[3]-self.icon.bitmap.get_height())/2))
		else:
			print "Icon not connected to object"

##### Main body of code #####

# Create and populate an icon list. This approach allows the addition of unlimited number of icons
icons = []
for file in os.listdir("/home/pi/bike_dashcam/media/"):
	if fnmatch.fnmatch(file, '*.png'):
		icons.append(Icon(file.split('.')[0]))

class VideoThread(threading.Thread):

	def __init__(self, output): #resolution):
		threading.Thread.__init__(self)
		self.output = output
	#	self.resolution = resolution

	def run(self):
		print "Starting video"
		self.start_vid()

	def start_vid(self):
		#camera.start_recording(self.output)#, resize=self.resolution)
		subprocess.call(["raspivid", "-o", self.output, "-t", "10000"])
		global busy
		busy = False

def start_video_callback():
	print "Callback triggered"
	camera.close()
	print "Camera closed"
	global busy
	busy = True
	screen.fill((255,0,0))
	pygame.display.update()
	new_video_thread = VideoThread("/home/pi/bike_dashcam/videos/video.h264")
	new_video_thread.start()

# List of buttons
buttons = [Button((0,0,50,50), icon_name='go', callback=start_video_callback)]

# Assign icons to buttons
for b in buttons:
	for i in icons:
		if b.icon_name == i.name:
			print b.icon_name
			b.icon = i
			b.icon_name = None

# Init GO button
go = buttons[0]

def stream_to_screen():
	stream = io.BytesIO()
        camera.capture(stream, use_video_port=True, format='raw')
	stream.seek(0)
	stream.readinto(yuv)
	stream.close()
	yuv2rgb.convert(yuv, rgb, size[0], size[1])
	img = pygame.image.frombuffer(rgb[0:(size[0]*size[1]*3)], size, 'RGB')
	screen.blit(img, ((width - img.get_width() ) / 2, (height - img.get_height()) / 2))

	go.draw(screen)	
	pygame.display.update()

global busy
busy = False
old_busy = True

while True:

	while True:
		for event in pygame.event.get():
			if(event.type is pygame.MOUSEBUTTONDOWN):
				pos = pygame.mouse.get_pos()
				print pos
				for b in buttons:
					if b.selected(pos):
						break
		break

	if (busy == False) and (old_busy == True):
		print "Camera enabled"
		camera = picamera.PiCamera()
		atexit.register(camera.close)
		camera.resolution = size
		camera.crop = (0.0,0.0,1.0,1.0)

	old_busy = busy
	# Stream to display
	while not busy:
		stream_to_screen()
		break

#       stream = io.BytesIO()
#	camera.capture(stream, use_video_port=True, format='raw')
#	stream.seek(0)
#	stream.readinto(yuv)
#	stream.close()
#	yuv2rgb.convert(yuv, rgb, size[0], size[1])
#	img = pygame.image.frombuffer(rgb[0:(size[0]*size[1]*3)], size, 'RGB')
#	screen.blit(img, ((width - img.get_width() ) / 2, (height - img.get_height()) / 2))
#
#	go.draw(screen)	
#	pygame.display.update()
