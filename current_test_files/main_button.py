from mqtt_as import MQTTClient, config
import asyncio
from machine import Pin

# Mosquitto connection and login information
config["ssid"] = "TskoliVESM"
config["wifi_pw"] = "Fallegurhestur"
config["server"] = "10.201.48.125"

TOPIC = "gdjsfsjdfdjdbxu" # Settu fyrstu fjóra stafinu úr kennitölunni þinni stað í X-anna
config["user"] = "gd"
config["password"] = "Pass1234"


turn_off_alarm_button = Pin(42, Pin.IN, Pin.PULL_DOWN)
button_value = 0
prev_button_value = 0

# function to send button value to alarm
async def sendir(client):
    global button_value
    global prev_button_value
    while True:
        # Checks if the button was pressed and ignores it if it was already pressed
        if button_value == 1 and prev_button_value == 0:
            signal = f"{turn_off_alarm_button.value()}".encode()
            print("Button pressed!!!!!")
        else: 
            signal = "0".encode()
        
        # updates the button values
        prev_button_value = button_value
        button_value = turn_off_alarm_button.value()
        # Sends the signal
        await client.publish(TOPIC, signal)
        await asyncio.sleep_ms(33)

async def main(client):
    # Connect to the internet
    await client.connect()
    
    # Makes the async task to send the signal
    asyncio.create_task(sendir(client))
    while True:
        await asyncio.sleep_ms(0)

# displays debug info relating to the mqtt connection   
MQTTClient.DEBUG = True

# Makes an instance of MQTTClient and sends in the settings
client = MQTTClient(config)

try:
    # Call the main function
    asyncio.run(main(client))
finally:
    client.close()
