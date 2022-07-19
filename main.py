import machine
import utime
import network
import time
import urequests
import gc
import dht
# imports
from credentials import SSID, PASSWORD, ADDR, ROOM

# node configuration


sensor = dht.DHT11(machine.Pin(13))  # dht11 init

SUCCESS = machine.Pin(16, machine.Pin.OUT)  # status pins
FAIL = machine.Pin(14, machine.Pin.OUT)

SUCCESS.value(1)  # set both pins to on; indicates system has started successfully
FAIL.value(1)
time.sleep(5)
FIRST_RUN = True  # if it is the first run, we will flash the success LED, otherwise success does not get flashed


def flash(pin, amount):
    for i in range(amount):
        pin.value(1)
        time.sleep(0.1)
        pin.value(0)
        time.sleep(0.1)


def get_data():
    sensor.measure()
    return {"temperature": sensor.temperature() - 5, "humidity": sensor.humidity(), "room": ROOM,
            "net_config": list(wlan.ifconfig())}  # the -5 is an offset. This is for a temperature sensor that is not
    # showing the right temperature. Calibrate and adjust the offset accordingly


def connect(wlan, ssid, password):
    wlan.active(True)
    wlan.connect(ssid, password)
    return wlan


def send(data):
    r = urequests.post(ADDR, json=data)
    print(f"Data sent, Response Code: {r.status_code}")
    del r


try:
    SUCCESS.value(0)  # turn off led's
    FAIL.value(0)

    wlan = connect(network.WLAN(network.STA_IF), SSID, PASSWORD)  # connect to the network
    wlan.scan()

    while True:

        if not wlan.isconnected():
            print("Connection to network failed. Trying again...")
            flash(FAIL, 4)
            FIRST_RUN = True
            wlan = connect(network.WLAN(network.STA_IF), SSID, PASSWORD)

        else:
            try:
                temp = get_data()
            except OSError as e:
                print("Sensor did not respond")
                continue

            print(f"Tempereature Logged: {temp}")
            print(f"Attempting to send to {ADDR}")
            try:
                send(temp)
                if FIRST_RUN:
                    flash(SUCCESS, 3)
                    FIRST_RUN = False
            except Exception as e:
                print(e)
                flash(FAIL, 1)
        time.sleep(10)
        gc.collect() # idk why this is needed, but there is memory problems when i dont manually collect garbage
except Exception as e:
    print("Fatal error.", e)
    FAIL.value(1)
