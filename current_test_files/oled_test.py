from machine import I2C, Pin
from ssd1309 import OLED_SSD1309
from mqtt_as import MQTTClient, config
import asyncio
import time

# Pin configuration for OLED screen
SCL_PIN = 5   
SDA_PIN = 4
SCREEN_WIDTH   = 128
SCREEN_HEIGHT  = 64
SCREEN_ADDRESS = 0x3C

i2c  = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400_000)
oled = OLED_SSD1309(SCREEN_WIDTH, SCREEN_HEIGHT, i2c, addr=SCREEN_ADDRESS)

# MQTT connection
config["ssid"] = "TskoliVESM"
config["wifi_pw"] = "Fallegurhestur"
config["server"] = "10.201.48.125" 
config["queue_len"] = 5

TOPIC = "gdjsfsjdfdjdbxu"
config["user"] = "gd"
config["password"] = "Pass1234"

def play_alarm:
    pass


# Clear the display, draw something, then push to screen
oled.fill(0)
oled.text("Hello, World!", 0, 0)
oled.text("test 1", 0, 10)
oled.show()

while True:
    

