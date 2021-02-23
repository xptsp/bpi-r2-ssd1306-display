FROM balenalib/raspberry-pi-debian-python:3.8-latest

RUN apt-get update && apt-get install -y build-essential git
RUN apt-get install libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev
RUN pip3 install Adafruit-SSD1306 Adafruit-BBIO Adafruit-GPIO Adafruit-PureIO psutil Pillow
RUN git clone https://github.com/xptsp/bpi-r2-ssd1306-display /stats

WORKDIR /stats
CMD python3 stats.py
