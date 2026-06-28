import machine
import network
import onewire
import ds18x20
import usocket as socket
import time
import json
import gc

from lib.umqtt.simple import MQTTClient

DEVICE_NAME = "Badtunna"
TEMP_TOPIC = b"temperature/badtunna"

WATCHDOG_TIMEOUT = 8388     # This seems to be max for some reason
PUBLISH_INTERVAL = 10
MAX_ERRORS = 20

#wdt = machine.WDT(timeout=WATCHDOG_TIMEOUT)


def load_config():
    with open("config.json") as f:
        return json.load(f)


def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
    if wlan.isconnected():
        return wlan
    print("Connecting WiFi...")
    wlan.connect(ssid, password)
    timeout = 20

    while timeout > 0:
        if wlan.isconnected():
            print("WiFi connected:", wlan.ifconfig())
            return wlan
        timeout -= 1
        time.sleep(1)
 #       wdt.feed()
    raise RuntimeError("WiFi connection failed")


def connect_mqtt(config):
    print("Connecting MQTT...")
    client = MQTTClient(
        DEVICE_NAME,
        config["mqtt"]["broker_url"],
        port=1883,
        user=config["mqtt"].get("username"),
        password=config["mqtt"].get("password"),
        keepalive=120
    )
    client.connect()
    print("MQTT connected")
    return client


def ensure_wifi(wlan, ssid, password):
    if wlan.isconnected():
        return wlan
    print("WiFi lost")
    try:
        wlan.disconnect()
    except:
        pass
    return connect_wifi(ssid, password)


def ensure_mqtt(client, config):
    try:
        client.check_msg()
        return client
    except:
        print("MQTT disconnected")
        try:
            client.disconnect()
        except:
            pass
        return connect_mqtt(config)


def create_sensor():
    ds_pin = machine.Pin(22)
    sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    roms = sensor.scan()
    if not roms:
        raise RuntimeError("No DS18B20 sensors found")
    print("Found sensors:", roms)
    return sensor, roms


def main():
    config = load_config()
    wlan = connect_wifi(
        config["wifi"]["ssid"],
        config["wifi"]["password"]
    )
    mqtt = connect_mqtt(config)
    sensor, roms = create_sensor()
    errors = 0

    while True:
        try:
  #          wdt.feed()
            wlan = ensure_wifi(
                wlan,
                config["wifi"]["ssid"],
                config["wifi"]["password"]
            )
            mqtt = ensure_mqtt(mqtt, config)
            sensor.convert_temp()
            time.sleep_ms(750)
            for rom in roms:
                temp = sensor.read_temp(rom)
                print(temp)

                mqtt.publish(
                    TEMP_TOPIC,
                    json.dumps({"temperature": temp})
                )
                
            errors = 0
            gc.collect()
            time.sleep(PUBLISH_INTERVAL)
        except Exception as e:
            errors += 1
            print("Loop error:", e)
            gc.collect()
            time.sleep(5)
            if errors >= MAX_ERRORS:
                print("Too many errors, rebooting...")
                machine.reset()

while True:
    try:
        time.sleep(5)   # 5 second delay until program starts
        main()
    except Exception as e:
        print("Fatal error:", e)
        time.sleep(5)
        machine.reset()