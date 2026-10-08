

# mqtt button test:
# delete later
'''
async def led_test(client):
    async for topic, message, _ in client.queue:
        button_pressed = int(message.decode())
        # If button is pressed flips led from on to off or vice versa
        if button_pressed == 1:
            print("button pressed!!!!!")
            change_led_state = not led.value()
            led.value(change_led_state)
        asyncio.sleep_ms(30000)
'''
        
# Subscribes to the mqtt topic
async def subscribe(client):
    while True:
        await client.up.wait()
        client.up.clear()
        # Topik-ið (eitt eða fleiri) sem á að gerast áskrifandi að
        await client.subscribe(TOPIC, 1)
        
        await client.subscribe(TOPIC_2, 1)
    
async def alarm():
    alarm_has_been_started = False
    while True:
        year, month, day, hours, minutes, seconds, weekday, _ = time.localtime()
        
        # formatts the numbers to add a 0 at the start if needed
        hours = str(hours)
        minutes = str(minutes)
        if len(minutes) < 2:
            minutes = "0" + minutes
        if len(hours) < 2:
            hours = "0" + hours
        
        # times at which the alarm plays
        wakeup_times = ["7:30", "8:30", "9:30"]
        
        
        '''
        async for topic, message, _ in client.queue:
            button_pressed = int(message.decode())
            # If button is pressed flips led from on to off or vice versa
            if button_pressed == 1:
                print("button pressed!!!!!")
                change_led_state = not led.value()
                led.value(change_led_state)
            asyncio.sleep_ms(20)
        '''
        
        #print(f"{hours}:{minutes}", "compared to: ", f"{wakeup_times[0]}")
        
        if f"{hours}:{minutes}" in wakeup_times and alarm_has_been_started == False:
            alarm_has_been_started = True
            # waits for the dfplayer to finish booting up and plays the song
            # in folder 01 and file 001.mp3
            await df.wait_available()
            await df.volume(10)
            await df.play(1, 1)
        await asyncio.sleep_ms(1000)
    
    async for topic, message, _ in client.queue:
        button_pressed = int(message.decode())
        # Turn off player if button is pressed:
        if button_pressed == 1:
            alarm_has_been_started = False
            await df.stop()
    

async def screen():
    while True:
        year, month, day, hours, minutes, seconds, weekday, _ = time.localtime()
        
        # formatts the numbers on screen to show a 0 at the start if needed
        hours = str(hours)
        minutes = str(minutes)
        if len(minutes) < 2:
            minutes = "0" + minutes
        if len(hours) < 2:
            hours = "0" + hours
        
        # Screen pins, dimentions and address
        SCL_PIN = 5
        SDA_PIN = 4
        SCREEN_WIDTH   = 128
        SCREEN_HEIGHT  = 64
        SCREEN_ADDRESS = 0x3C

        i2c  = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400_000)
        oled = OLED_SSD1309(SCREEN_WIDTH, SCREEN_HEIGHT, i2c, addr=SCREEN_ADDRESS)

        # Clear the display, draw something, then push to screen
                    
        oled.fill(0)
        oled.text("-------------------------", 0, 16)
        oled.text("-------------------------", 0, 48)
        oled.text(f"{hours}:{minutes}", 42, 32)
        oled.show()    
        
        await asyncio.sleep_ms(30000)

async def main(client):
    
    # connect to the internet
    await client.connect()
    
    # runs async functions
    asyncio.create_task(subscribe(client))
    asyncio.create_task(alarm())
    asyncio.create_task(screen())

    while True:
        await asyncio.sleep_ms(0)

# Displays MQTTClient debug info
MQTTClient.DEBUG = True
#Creates an instance of mqttclient and sends it the configurations
client = MQTTClient(config)

try:
    asyncio.run(main(client))
finally:
    client.close()
