from machine import Pin, ADC
from mqtt_as import MQTTClient, config
import asyncio

takki = Pin(14, Pin.IN, Pin.PULL_DOWN)

# WIFI stillingar
config["ssid"] = "TskoliVESM"
config["wifi_pw"] = "Fallegurhestur"

# MQTT þjónninn
config["server"] = "10.201.48.125" # eða broker.emqx.io (þarf að vera það sama á sendir og móttakara)

# TOPICS
TOPIC = "gdjsfsjdfdjdbxu" # Settu fyrstu fjóra stafinu úr kennitölunni þinni stað í X-anna

async def sendir(client):
    while True:
        # Skilaboðin sem á að senda verða bytes, til þess þarf encode, sérstaklega ef senda á íslenska stafi
        if takki.value()==1:
            skilabod="1".encode()
            print(f"Ýtti á takka: {skilabod}" )
        # Skilaboðin send
            await client.publish(TOPIC, skilabod)
        # Sendi á tveggja sekúnda fresti
            await asyncio.sleep_ms(2000)
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
