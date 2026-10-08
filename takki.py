from machine import Pin, ADC
from mqtt_as import MQTTClient, config
import asyncio
# Takkinn er tengdur við GPIO 14
# Pin.IN = ESP32 les stöðu takkans
# Pin.PULL_DOWN = pinninn er 0 þegar ekki er ýtt á takkann
takki = Pin(14, Pin.IN, Pin.PULL_DOWN)
# Nafnið á Wi-Fi netinu
config["ssid"] = "TskoliVESM"

# Lykilorðið á Wi-Fi netinu
config["wifi_pw"] = "Fallegurhestur"


# IP-talan á MQTT brokerinum
config["server"] = "10.201.48.125"

# Hversu mörg skilaboð mega bíða í biðröðinni
config["queue_len"] = 5


# MQTT topic sem skilaboðin eru send á
# NiceGUI forritið þarf að nota sama topic
TOPIC = "gdjsfsjdfdjdbxu"

# Notandanafn fyrir MQTT brokerinn
config["user"] = "gd"
# Lykilorð fyrir MQTT brokerinn

config["password"] = "Pass1234"

async def sendir(client):
    while True:
        # Skilaboðin sem á að senda verða bytes, til þess þarf encode, sérstaklega ef senda á íslenska stafi
        if takki.value()==1:
            skilabod="1".encode()
            print(f"Ýtti á takka: {skilabod}" )
        # Skilaboðin send
            await client.publish(TOPIC, skilabod)
          # Þetta kemur í veg fyrir að sama ýting sendi
            # mörg skilaboð
            while takki.value() == 1:
                # Athugar stöðu takkans á 20 millisekúndna fresti
                await asyncio.sleep_ms(20)
        await asyncio.sleep_ms(20)
        
async def main(client):
    # tengjast við þráðlausa netið
    await client.connect()
    # búa til task
    asyncio.create_task(sendir(client))
    while True:
        # Hér kæmi kóði sem á ekki að keyra async
        await asyncio.sleep_ms(0)

# Sýnir ýmsar upplýsingar eins og t.d. varðandi nettenginguna og minnisnotkun  
MQTTClient.DEBUG = True

# Búa til tilvik af MQTTClient og senda inn stillingarnar
client = MQTTClient(config)

try:
    # Ræsa async main fallið og senda þangað tilvik af client-num
    asyncio.run(main(client))
finally:
    client.close()
