#!/usr/bin/python3
###################################################################################
# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###################################################################################
import os
import time
import socket
import fcntl
import struct
import psutil
import signal
import sys
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

###################################################################################
# Change these variables to reflect which network adapter to use during this check
###################################################################################
wan_interface = "wan"
w24_interface = "wlp1s0"
w5G_interface = "wlp1s0"
vpn_interface = "vpn_in"

###################################################################################
# Setup for script execution:
###################################################################################
# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Initialize library.
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_bus=2)
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Load default font.
font = ImageFont.load_default()

###################################################################################
# Load images once into memory:
###################################################################################
globe = Image.open('images/globe.png').convert('1')
wifi  = Image.open('images/wifi.png').convert('1')
no_wifi = Image.open('images/no-wifi.png').convert('1')
vpn   = Image.open('images/vpn.png').convert('1')

###################################################################################
# Function to get IP address about a specific network adapter:
###################################################################################
def get_ip_address(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack('256s', ifname[:15].encode('UTF-8'))
	)[20:24])

###################################################################################
# Our signal handler to clear the screen upon exiting the script:
###################################################################################
def signal_handler(sig, frame):
	disp.clear()
	disp.display()
	sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

###################################################################################
# Main loop which shows information about our computer:
###################################################################################
while True:
	# Draw a black filled box to clear the image.
	draw.rectangle((0,0,width,height), outline=0, fill=0)
	
	###############################################################################
	# Show the globe symbol if the WAN interface up and cable connected.
	###############################################################################
	try:
		with open("/sys/class/net/" + wan_interface + "/operstate") as f:
			if f.read().strip() != "up":
				throw
		image.paste(globe, (32 * 0, 0))
		draw.text((0, 30), "WAN:  " + get_ip_address(wan_interface),  font=font, fill=255)
	except:
		draw.text((0, 30), "Cable Disconnected",  font=font, fill=255)

	###############################################################################
	# Show the globe symbol if the 2.4Ghz wifi interface is up.
	###############################################################################
	draw.text((32 * 1, 16), "2.4G",  font=font, fill=255)
	try:
		with open("/sys/class/net/" + w24_interface + "/operstate") as f:
			if f.read().strip() != "up":
				throw
		image.paste(wifi, (32 * 1 + 4, 0))
	except:
		image.paste(no_wifi, (32 * 1 + 4, 0))

	###############################################################################
	# Show the globe symbol if the 5Ghz wifi interface is up.
	###############################################################################
	draw.text((32 * 2, 16), "5GHz",  font=font, fill=255)
	try:
		with open("/sys/class/net/" + w5G_interface + "/operstate") as f:
			if f.read().strip() != "up":
				throw
		image.paste(wifi, (32 * 2 + 4, 0))
	except:
		image.paste(no_wifi, (32 * 2 + 4, 0))

	###############################################################################
	# Show the VPN symbol if the VPN_IN interface is up.
	###############################################################################
	try:
		with open("/sys/class/net/" + vpn_interface + "/operstate") as f:
			if f.read().strip() != "up":
				throw
		image.paste(vpn, (32 * 3, 0))
	except:
		pass

	###############################################################################
	# Write the CPU load values
	###############################################################################
	load = os.getloadavg()
	draw.text((0, 38), "Load: " + '{:.2f}'.format(load[0]) + "," + '{:.2f}'.format(load[1]) + "," + '{:.2f}'.format(load[2]),  font=font, fill=255)

	###############################################################################
	# Write the available and total memory
	###############################################################################
	mem = psutil.virtual_memory()
	total = int(mem.total / 1024 / 1024)
	used = total - int(mem.available / 1024 / 1024)
	percent = int(used / total * 100)
	if used < 10000:
		s1 = "{:4d}M".format(used)
	else:
		s1 = "{:2.1f}G".format(used / 1024)
	if total < 10000:
		s2 = "{:4d}M".format(total)
	else:
		s2 = "{:2.1f}G".format(total / 1024)
	draw.text((0, 46), "Mem:  " + s1 + "/" + s2 + " " + "{:2d}".format(percent) + "%", font=font, fill=255)

	###############################################################################
	# Write the available and total disk space
	###############################################################################
	mem = psutil.disk_usage('/')
	total = int(mem.total / 1024 / 1024)
	used = total - int(mem.free / 1024 / 1024)
	percent = int(used / total * 100)
	if used < 10000:
		s1 = "{:4d}M".format(used)
	else:
		s1 = "{:2.1f}G".format(used / 1024)
	if total < 10000:
		s2 = "{:4d}M".format(total)
	else:
		s2 = "{:2.1f}G".format(total / 1024)
	draw.text((0, 54), "Disk: " + s1 + "/" + s2 + " " + "{:2d}".format(percent) + "%", font=font, fill=255)
	
	###############################################################################
	# Display image.
	###############################################################################
	disp.image(image)
	disp.display()
	time.sleep(.1)
