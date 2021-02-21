# BPI-R2 stats python program for SSD1306 OLED display

## Intro 
The code found in this repo is based on the [stats.py](https://github.com/adafruit/Adafruit_Python_SSD1306/blob/master/examples/stats.py) file found in Adafruit's Python SSD1306 repo.  It has been customized to use Python calls only, thereby freeing it from use of Bash calls.  It has only be tested on a Debian 10 install on the Banana Pi R2, and may require modifications to work on other OSes.

## Display In Action
![](https://github.com/xptsp/bpi-r2-ssd1306-display/blob/master/display_in_action.jpg)

## Script Customization
Inside the `stats.py` script, there are several lines to change.  These lines control which interface each of the 4 icons represent.
```
wan_interface = "wan"
w24_interface = "wlp1s0"
w5G_interface = "wlp1s0"
vpn_interface = "vpn_in"
```
Further modification is planned to modulize the text and images.

## Installation
Install required system packages:
```
apt install -y python3-pip libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
```

Install required Python packages via PIP:
```
python3 -m pip install --upgrade pip wheel setuptools
python3 -m pip install Adafruit-SSD1306 Adafruit-BBIO Adafruit-GPIO Adafruit-PureIO Pillow psutil
```

Clone the repo, install  and enable the service file:
```
git clone https://github.com/xptsp/bpi-r2-ssd1306-display /opt/stats
cp /opt/stats/stats.service /etc/systemd/system/stats.service
systemctl enable stats
systemctl start stats
```
