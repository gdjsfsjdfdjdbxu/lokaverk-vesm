from mqtt_as import MQTTClient, config
import asyncio
from machine import Pin, ADC
import time
from lib.dfplayer import DFPlayer

# Mqtt connection and login information
config["ssid"] = "TskoliVESM"
config["wifi_pw"] = "Fallegurhestur"
config["server"] = "10.201.48.125" 
config["queue_len"] = 5

TOPIC = "gdjsfsjdfdjdbxu"
config["user"] = "gd"
config["password"] = "Pass1234"

# smt idk
year, month, day, hours, minutes, seconds, weekday, _ = time.localtime()
print(f"{hours:02}:{minutes:02}:{seconds:02}")

# dfplayer variables
df = DFPlayer(2)  # using UART 
df.init(tx=17, rx=16)  # tx á esp tengist í rx á mp3



### Code from verk-3, might be useful later as a reference

'''

async def mottakari(client):
    # skilaboðin berast í biðröð (e. queue) sem við sækjum þau svo úr
    async for topic, skilabod, _ in client.queue:
        hallo, tala = skilabod.decode().split()
        # ef nota á töluna þarf að setja hana í int fallið
        tala = int(tala)
        print(f"TOPIC: {topic.decode()}, texti: {hallo}, tala: {tala}")

'''

async def led_test(client):
    async for topic, message, _ in client.queue:
        button_pressed = int(message.decode())
        # If button is pressed flips led from on to off or vice versa
        if button_pressed == 1:
            print("button pressed!!!!!")
            change_led_state = not led.value()
            led.value(change_led_state)
        asyncio.sleep_ms(0)
        
        
# Fallið sér um að gerast ákrifandi að topic-um og viðhalda áskriftinni ef tenging tapast
async def subscribe(client):
    while True:
        await client.up.wait()
        client.up.clear()
        # Topik-ið (eitt eða fleiri) sem á að gerast áskrifandi að
        await client.subscribe(TOPIC, 1) 
        # await client.subscribe(TOPIC_2, 1)
    
async def alarm():
    await df.wait_available()  # optional; making sure DFPlayer finished booting
    await df.volume(5)
    await df.play(1, 1)  # folder 1, file 1
    await asyncio.sleep_ms(0)  # þarf ekki í þessu tilfelli en má vera
    

async def main(client):
    # connect to the internet
    await client.connect()
    # makes async tasks
    asyncio.create_task(subscribe(client))
    asyncio.create_task(led_test(client))
    asyncio.create_task(alarm())

    while True:
        await asyncio.sleep_ms(0)

# Displays MQTTClient debug info
MQTTClient.DEBUG = True
#Creates an instance of mqttclient and sends it the configurations
client = MQTTClient(config)

try:
    # Calls the main function
    asyncio.run(main(client))
finally:
    client.close()
