#AWS MQTT client cert example for esp8266 or esp32 running MicroPython 1.9
from umqtt.robust import MQTTClient
import time
import network
import machine
from machine import Pin, ADC
from time import sleep
import usocket as socket

light_sensor = ADC(0)
global light_sensor_value
global state

led = Pin(2, Pin.OUT, value=0)

#Certs for ESP8266
CERT_FILE = "/flash/8266-01.cert.der"
KEY_FILE = "/flash/8266-01.key.der"

#if you change the ClientId make sure update AWS policy
MQTT_CLIENT_ID = "basicPubSub"
MQTT_PORT = 8883

MQTT_KEEPALIVE_INTERVAL = 45
THING_NAME = "8266-01"
SHADOW_GET_TOPIC = "$aws/things/" + THING_NAME + "/shadow/get"
SHADOW_UPDATE_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update"
SHADOW_UPDATE_ACCEPTED_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update/accepted"
SHADOW_UPDATE_REJECTED_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update/rejected"
SHADOW_STATE_DOC_LED_ON = """{"state" : {"desired" : {"LED" : "ON"}}}"""
SHADOW_STATE_DOC_LED_OFF = """{"state" : {"desired" : {"LED" : "OFF"}}}"""
RESPONSE_RECEIVED = False

#if you change the topic make sure update AWS policy
MQTT_TOPIC = "esp8266-topic"

#Change the following three settings to match your environment
MQTT_HOST = "a1mb8wmxclan82-ats.iot.us-east-1.amazonaws.com"
WIFI_SSID = "ENOT"
WIFI_PW = "0637087396"

mqtt_client = None

def pub_msg():
    global mqtt_client

    while True:
        try:
            mqtt_client.publish(SHADOW_GET_TOPIC, str(read_sensor_value()))
            #mqtt_client.publish(SHADOW_GET_TOPIC, "{\n" + "\t" + "\"" + "default" + "\"" + ": " + "\"" + read_sensor_value() + "\"" + "\n" + "}")
            #print("Sent: " + "{\n" + "\t" + "\"" + "default" + "\"" + ": " + "\"" + read_sensor_value() + "\"" + "\n" + "}")
            sleep(10)
        except Exception as e:
            print("Exception publish: " + str(e))
            raise

def sub_cb(topic, msg):
    print(msg)
    try:
        if int(msg) < 200:
            led.value(0)
            state = 1
        else:
            led.value(1)
            state = 0
    except:
        print("The message is None or message format is not supported")

#def mqtt_topic_get():
#    global mqtt_client
#    connect_mqtt()
#    mqtt_client.subscribe(SHADOW_GET_TOPIC)
#    print("Subscribed to %s topic" % (SHADOW_GET_TOPIC))

#    try:
#        while 1:
            #micropython.mem_info()
#            c.wait_msg()
#    finally:
#        c.disconnect()


def connect_mqtt():
    try:
        with open(KEY_FILE, "r") as f:
            key = f.read()

        print("MQTT received KEY")

        with open(CERT_FILE, "r") as f:
            cert = f.read()

        print("MQTT received CERTIFICATE")

        mqtt_client = MQTTClient(client_id=MQTT_CLIENT_ID, server=MQTT_HOST, port=MQTT_PORT, keepalive=5000, ssl=True, ssl_params={"cert":cert, "key":key, "server_side":False})
        mqtt_client.connect()
        mqtt_client.set_callback(sub_cb)
        print("MQTT is connected")
        mqtt_client.subscribe(SHADOW_GET_TOPIC)
        print("Subscribed to %s topic" % (SHADOW_GET_TOPIC))
        while True:
            mqtt_client.publish(SHADOW_UPDATE_TOPIC, str(read_sensor_value()))
            mqtt_client.wait_msg()

    except Exception as e:
        print('Cannot connect to MQTT ' + str(e))
        raise

def led_state(led):
    print(led.value())

def read_sensor_value():
    light_sensor_value = light_sensor.read()
    return str(light_sensor_value)

def connect_wifi(ssid, pw):
    wlan = network.WLAN(network.STA_IF)

    if(wlan.isconnected()):
        wlan.disconnect()
    nets = wlan.scan()

    if not wlan.isconnected():

        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PW)
        while not wlan.isconnected():
            pass
    print("Connected as:", wlan.ifconfig())

#start execution
try:
    print("Connecting to WIFI...")
    connect_wifi(WIFI_SSID, WIFI_PW)
    print("Connecting to MQTT...")
    connect_mqtt()
    #print("Publishing")
    #pub_msg()
    print("OK")
    #led_state(led)
    #mqtt_topic_get()

except Exception as e:
    print(str(e))
