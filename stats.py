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

use_img=False
use_img=True

use_disp=False
use_disp=True

import os
import time
import socket
import fcntl
import struct
import psutil
import signal
import sys
#import Adafruit_GPIO.SPI as SPI

if use_disp:
    import Adafruit_SSD1306

if use_img:
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont

iconpath = os.path.dirname(__file__)+"/images"
iconwidth = 16

###################################################################################
# Change these variables to reflect which network adapter to use during this check
###################################################################################
wan_interface = "wan"
w24_interface = "wlp1s0"
w5G_interface = "wlp1s0"
vpn_interface = "vpn_in"

i2cbus=2
disp_w=128
disp_h=64

if use_disp:
    # Initialize library.
    disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_bus=i2cbus)
    disp.begin()

    # Clear display.
    disp.clear()
    disp.display()

if use_img:
    if use_disp:
        width = disp.width
        height = disp.height
    else:
        width=disp_w
        height=disp_h

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
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
#    #16x16 icons
#    globe = Image.open(iconpath+"/"+'earth16w.png').convert('1')
#    wifi = Image.open(iconpath+"/"+'wifi16w.png').convert('1')
#    phone = Image.open(iconpath+"/"+'phone16w.png').convert('1')
#    no_wifi = Image.open(iconpath+"/"+'no16w.png').convert('1')
#    vpn   = Image.open(iconpath+"/"+'vpn16w.png').convert('1')

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
    if use_disp:
        disp.clear()
        disp.display()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

###################################################################################
# Main loop which shows information about our computer:
###################################################################################
while True:
    ###############################################################################
    # Show the globe symbol if the WAN interface up and cable connected.
    ###############################################################################
    wan_txt="WAN: "
    wan_ico=None
    try:
        with open("/sys/class/net/" + wan_interface + "/operstate") as f:
            if f.read().strip() != "up":
                throw
        wan_ico=globe
        wan_txt+= get_ip_address(wan_interface)
    except:
        wan_txt+="disconnected"
    print(wan_txt)


    ###############################################################################
    # Show the globe symbol if the 2.4Ghz wifi interface is up.
    ###############################################################################
    wifi24_txt="2G4: "
    wifi24_ico=None
    try:
        with open("/sys/class/net/" + w24_interface + "/operstate") as f:
            if f.read().strip() != "up":
                throw
        wifi24_ico=wifi
        wifi24_txt+="up"
    except:
        wifi24_ico=no_wifi
        wifi24_txt+="none"
    print(wifi24_txt)

    ###############################################################################
    # Show the globe symbol if the 5Ghz wifi interface is up.
    ###############################################################################
    wifi5_txt="5G: "
    wifi5_ico=None
    try:
        with open("/sys/class/net/" + w5G_interface + "/operstate") as f:
            if f.read().strip() != "up":
                throw
        wifi5_ico=wifi
        wifi5_txt+="up"
    except:
        wifi5_ico=no_wifi
        wifi5_txt+="none"
    print(wifi5_txt)

    ###############################################################################
    # Show the VPN symbol if the VPN_IN interface is up.
    ###############################################################################
    vpn_ico=None
    try:
        with open("/sys/class/net/" + vpn_interface + "/operstate") as f:
            if f.read().strip() != "up":
                throw
        vpn_ico=vpn
    except:
        #vpn_ico=vpn
        pass

    phone_ico=None
    #phone_ico=phone
    ###############################################################################
    # Write the CPU load values
    ###############################################################################
    load = os.getloadavg()
    load_txt="Load: " + '{:.2f}'.format(load[0]) + "," + '{:.2f}'.format(load[1]) + "," + '{:.2f}'.format(load[2])
    print(load_txt)

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
    mem_txt="Mem:  " + s1 + "/" + s2 + " " + "{:2d}".format(percent) + "%"
    print(mem_txt)

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
    disk_txt="Disk: " + s1 + "/" + s2 + " " + "{:2d}".format(percent) + "%"
    print(disk_txt)

    ###############################################################################
    # Generate image.
    ###############################################################################
    if use_img:
        # Draw a black filled box to clear the image.
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        if wan_ico:
           image.paste(wan_ico, ((iconwidth + 2) * 0, 0))
        if wifi24_ico:
            image.paste(wifi24_ico, ((iconwidth + 2) * 1, 0))
        draw.text((iconwidth * 1 + 4, 16), "2G",  font=font, fill=255)
        if wifi5_ico:
            image.paste(wifi5_ico, ((iconwidth + 2) * 2, 0))
        draw.text((iconwidth * 2 + 6, 16), "5G",  font=font, fill=255)
        if phone_ico:
            image.paste(phone_ico, ((iconwidth + 2) * 3, 0))

        if iconwidth < 24: #128/5=~25;-2=23
            if vpn_ico:
                image.paste(vpn_ico, ((iconwidth + 2) * 4, 0))
        if iconwidth < 20: #128/6=~21;-2=19
            if vpn_ico:
                image.paste(vpn_ico, ((iconwidth + 2) * 4, 0))

        draw.text((0, 30), wan_txt,  font=font, fill=255)
        draw.text((0, 38), load_txt,  font=font, fill=255)
        draw.text((0, 46), mem_txt, font=font, fill=255)
        draw.text((0, 54), disk_txt, font=font, fill=255)
        if use_disp:
            ###############################################################################
            # Display image.
            ###############################################################################
            disp.image(image)
            disp.display()
        else:
            image.save('/home/frank/stats.png')
    time.sleep(5)
