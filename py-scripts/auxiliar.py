import time
import json
from termcolor import colored
import paho.mqtt.client as mqtt
from geopy.distance import distance
import threading
import subprocess

# this program should public the posts information to the "192.168.98.1", 1883, 60 and public the content of the file "posts_coordinaates.json"

broker_address = "192.168.98.1"
broker_port = 1883
topic = "posts_info"

obu_lat = 0
obu_lon = 0

client = mqtt.Client()
client.connect(broker_address, broker_port, 60)
client.loop_start()

POSTS_status = {}

with open('posts_coordinates.json') as json_file:
    posts = json.load(json_file)

def on_connectLSM(client, userdata, flags, rc):
    print("Connected to rsus with result code "+str(rc))
    client.subscribe("all/lsm")

def on_messageLSM(client, userdata, msg):
    message = json.loads(msg.payload)
    id = str(message["station_id"])
    intensity = message["intensity"]
    dest_stations = message["dest_stations"]
    POSTS_status[id]['intensity'] = intensity
    POSTS_status[id]['target_posts'] = dest_stations
    

#LSM broker
clientLSM = mqtt.Client()
clientLSM.on_connect = on_connectLSM
clientLSM.on_message = on_messageLSM
clientLSM.connect("192.168.98.1")

threading.Thread(target=clientLSM.loop_forever).start()
with open('posts_coordinates.json') as json_file:
    data = json.load(json_file)
    POSTS_status = data

while True:
    with open('posts_coordinates.json') as json_file:
        data = json.load(json_file)
        POSTS_status = data
        client.publish(topic, json.dumps(data))
        # print(colored("Published posts information to the MQTT broker", "green"))
    time.sleep(1)
