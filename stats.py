#!/usr/bin/python3
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
import os
import time
import socket
import fcntl
import struct
import psutil
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

def get_ip_address(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack('256s', ifname[:15].encode('UTF-8'))
	)[20:24])

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

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding + 32
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

# Load images
power = Image.open('power.png').convert('1')
globe = Image.open('globe.png').convert('1')
wifi  = Image.open('wifi.png').convert('1')
vpn   = Image.open('vpn.png').convert('1')

while True:
	# Draw a black filled box to clear the image.
	draw.rectangle((0,0,width,height), outline=0, fill=0)
	
	# Show the globe symbol if the WAN interface up and cable connected.
	try:
		with open("/sys/class/net/wan/operstate") as f:
			state = f.read().strip()
		if state == "up":
			image.paste(globe, (32 * 0, 0))
	except:
		pass

	# Show the globe symbol if the WAN interface up and cable connected.
	try:
		with open("/sys/class/net/w24g_norm/operstate") as f:
			state = f.read().strip()
		if state == "up":
			image.paste(wifi, (32 * 1, 0))
	except:
		pass

	# Show the globe symbol if the WAN interface up and cable connected.
	try:
		with open("/sys/class/net/w5g_norm/operstate") as f:
			state = f.read().strip()
		if state == "up":
			image.paste(wifi, (32 * 2, 0))
	except:
		pass

	# Show the VPN symbol if the VPN_IN interface up and cable connected.
	try:
		with open("/sys/class/net/vpn_in/operstate") as f:
			state = f.read().strip()
		if state == "up":
			image.paste(vpn, (32 * 3, 0))
	except:
		pass

	# Write the IP address obtained from the WAN adapter:
	draw.text((x, top),       "WAN:  " + get_ip_address("wan"),  font=font, fill=255)
	
	# Write the CPU load values:
	load = os.getloadavg()
	txt = '{a:.2f}'
	draw.text((x, top + 8),  "Load: " + txt.format(a = load[0]) + "," + txt.format(a = load[1]) + "," + txt.format(a = load[2]),  font=font, fill=255)

	# Write the available and total memory:
	mem = psutil.virtual_memory()
	total = int(mem.total / 1024 / 1024)
	free = total - int(mem.available / 1024 / 1024)
	percent = int(free / total * 100)
	draw.text((x, top + 16), "Mem:  " + str(free) + "M/" + str(total) + "M  " + str(percent) + "%", font=font, fill=255)

	# Write the available and total disk space:
	mem = psutil.disk_usage('/')
	total = int(mem.total / 1024 / 1024)
	free = int(mem.free / 1024 / 1024)
	percent = int(free / total * 100)
	draw.text((x, top + 24), "Disk: " + str(free) + "M/" + str(total) + "M " + str(percent) + "%", font=font, fill=255)
	
	# Display image.
	disp.image(image)
	disp.display()
	time.sleep(1)
