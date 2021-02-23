# BPI-R2 stats python program for SSD1306 OLED display

## Intro
The code found in this repo is based on the [stats.py](https://github.com/adafruit/Adafruit_Python_SSD1306/blob/master/examples/stats.py) file
found in Adafruit's Python SSD1306 repo.  It has been customized by xptsp to use Python calls only, thereby freeing it from use of Bash calls.
It has only be tested on a Debian 10 install on the Banana Pi R2, and may require modifications to work on other OSes, kernels, boards, and/or architectures.

## Tested With
- [Banana Pi R2](http://www.banana-pi.org/r2.html)
- [Frank-W's kernel 5.10.11](https://github.com/frank-w/BPI-R2-4.14) - branch **5.10-main**
- [Frank-W's Debian 10](https://drive.google.com/file/d/1VbV_IaUy92p1bIrd74sahs77LQNSQEVd/view?usp=sharing)
- [SSD1306 Display](https://www.amazon.com/gp/product/B076PM5ZSJ)

## Expected GPIO configuration
- VCC is on pin 1 (3.3V)
- GND is on pin 9
- SDA on pin 27
- SCL on pin 28

## Display In Action
![](https://github.com/xptsp/bpi-r2-ssd1306-display/blob/master/images/display_in_action.jpg)

## Script Customization
Inside the `stats.py` script, there are several lines to change.  These lines control which interface each of the 4 icons represent.
```
wan_interface = "wan"
w24_interface = "wlp1s0"
w5G_interface = "wlp1s0"
vpn_interface = "vpn_in"
```
Further modification is planned to modularize the text and images.

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
