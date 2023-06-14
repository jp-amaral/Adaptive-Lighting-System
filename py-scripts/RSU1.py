import paho.mqtt.client as mqtt
import time
from datetime import datetime
import json
import random
from geopy.distance import distance
from termcolor import colored
import math as Math
import threading

class post:
    def __init__(self, x, y):
        self.x = x
        self.y = y

ID = 1
post = post(40.636032, -8.646632)
BIAS = 2.8
LAMPS = {}

MY_STATUS = "dimmed"
MY_INTENSITY = 20
RADIUS = 70
OBUS = {}

last_3_distances = []

def on_connectLamps(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("posts_info")

def on_messageLamps(client, userdata, msg):
    global LAMPS
    message = json.loads(msg.payload)
    LAMPS = message

def on_connectObu(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("vanetza/out/cam")

def on_connectRsu(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("all/lsm")
    


def on_messageRsu(client, userdata, msg):
    message = json.loads(msg.payload)
    if(message["station_id"] == ID):
        return
    dest_stations = message["dest_stations"]
    for key, value in dest_stations.items():
        if key == str(ID):
            # if MY_INTENSITY < value:
            MY_INTENSITY = value
            print(colored("Intensity received: ", "yellow"), colored(MY_INTENSITY, "yellow"))

def on_messageObu(client, userdata, msg):
    global MY_STATUS, MY_INTENSITY, BIAS, OBUS

    message = json.loads(msg.payload)
    longitude = message["longitude"]
    latitude = message["latitude"]
    speed = message["speed"]
    obu_id = message["stationID"]

    distance_between_car_and_post = round(distance((latitude, longitude), (post.x, post.y)).meters,2)

    if(distance_between_car_and_post > 70):
        # print(colored("Distance is: ", "red"), colored(distance_between_car_and_post, "red"))
        return
    # else:
    #     print(colored("Distance is: ", "green"), colored(distance_between_car_and_post, "green"))

    # last_3_distances.append(distance_between_car_and_post)
    # if len(last_3_distances) > 3:
    #     last_3_distances.pop(0)

    if(obu_id not in OBUS):
        OBUS[obu_id] = {"longitude": longitude, "latitude": latitude, "speed": speed}
        return
    else:
        OBUS[obu_id]["longitude"] = longitude
        OBUS[obu_id]["latitude"] = latitude
        OBUS[obu_id]["speed"] = speed

    #out of all the obus, get the closest distance
    closest_distance, closest_obu = get_closest_obu(OBUS, post.x, post.y)

    facing = facing_post(last_3_distances)

    print(colored("Distance between OBU ", "blue"), obu_id, colored(" and post: ", "blue"), closest_distance)
    print(colored("Not facing post: ", "blue"), facing)
    print(colored("Speed: ", "blue"), speed)

    if(MY_STATUS == "on"):
        print(colored("My status: ", "green"), colored(MY_STATUS, "green"))
    else:
        print(colored("My status: ", "red"), colored(MY_STATUS, "red"))

    time_to_arrival = [round(calc_interval(closest_distance, speed),2)]
    print(colored("Time to arrival: ", "green"), time_to_arrival)
    # if(not facing):
    #     time_to_arrival = 0
    iluminacao = calc_iluminacao(closest_distance,speed, BIAS, facing)
    MY_INTENSITY = iluminacao

    if iluminacao > 20 and MY_STATUS == "dimmed":
        MY_STATUS = "on"
    
    elif iluminacao <= 20 and MY_STATUS == "on":
        MY_STATUS = "dimmed"

    print(colored("Iluminacao: ", "yellow"), colored(iluminacao, "yellow"))  
    print("\n")

    times = get_times_to_arrival()
    intensities = get_intensities(times, BIAS)
    out_message = construct_message([2], MY_INTENSITY, times)
    publish_lsm(out_message)
    
def publish_lsm(message):
    clientRsu.publish("all/lsm", message) #lsm = light support message
    print("LSM published")


def calc_iluminacao(distance, speed, bias, facing_post):
    tempo = calc_interval(distance, speed)
    # if(not facing_post):
    #    bias = 2
    luminosidade = 1/tempo*100*bias

    if luminosidade > 100:
        luminosidade = 100

    if luminosidade <20:
        luminosidade = 20

    if distance < 20:
        return 100
    
    return Math.ceil(luminosidade)

def calc_interval(distance, speed):
    # Converter a speed para metros por segundo
    speed_ms = speed * (1000/3600)

    # Calcular o tempo em segundos
    tempo = distance / speed_ms
    return tempo

def facing_post(last_3_distances):
    if len(last_3_distances) == 3:
        if last_3_distances[0] > last_3_distances[1] and last_3_distances[1] > last_3_distances[2]:
            return True
    return False

def construct_message(destination, intensity, intensities):
    f = open('./out_lsm.json')
    m = json.load(f)
    m["dest_stations"] = intensities
    m["intensity"] = intensity
    m["station_id"] = ID
    m["station_latitude"] = post.x
    m["station_longitude"] = post.y
    # m["time_to_arrival"] = time_to_arrival
    now = datetime.now()
    m["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S:%f")
    m = json.dumps(m)
    return m

def get_post_ids():
    global LAMPS
    if LAMPS == {}:
        return []
    ids = []
    for key, value in LAMPS.items():
        # if(post.x != value[0] and post.y != value[1]):
            #check if lamp is within radius
        # if distance((post.x, post.y), (value['Latitude'], value['Longitude'])).meters < RADIUS:
        ids.append(key)
    return ids

def get_times_to_arrival():
    global LAMPS, OBUS, RADIUS
    #for all the LAMPS, calculate the time to arrival of the closest obu
    times = {}
    for key, value in LAMPS.items():
        lat = value['Latitude']
        lon = value['Longitude']
        distance, obu_id = get_closest_obu(OBUS, lat, lon)
        # if distance < RADIUS:
        time_to_arrival = round(calc_interval(distance, OBUS[obu_id]["speed"]),2)
        #get the time right now as a string with miliseconds in the format HHMMSSMS
        now = datetime.now()
        times[key] = [time_to_arrival, now.strftime("%Y%m%d%H%M%S%f")]
    
    # print(times)
    return times

def intensity_on_time(tempo, bias):
    # if(not facing_post):
    #    bias = 2
    luminosidade = 1/tempo*100*bias

    if luminosidade > 100:
        luminosidade = 100

    if luminosidade <20:
        luminosidade = 20
    
    return Math.ceil(luminosidade)


def get_intensities(times, bias):
    intensities = {}
    for key, value in times.items():
        temp = intensity_on_time(value[0], bias)
        if (temp > 20):
            intensities[key] = [temp, value[1]]
        # intensities[key] = intensity_on_time(value, bias)

    print(intensities)
    return intensities

def get_closest_obu(OBUS, post_lat, post_long):
    closest_distance = 100000
    closest_obu = -1
    for key, value in OBUS.items():
        obu_lat = value['latitude']
        obu_long = value['longitude']
        distance_between_car_and_post = round(distance((obu_lat, obu_long), (post_lat, post_long)).meters,2)
        if distance_between_car_and_post < closest_distance:
            closest_distance = distance_between_car_and_post
            closest_obu = key
    return closest_distance, closest_obu


clientCams = mqtt.Client()
clientCams.on_connect = on_connectObu
clientCams.on_message = on_messageObu
clientCams.connect("192.168.98.10", 1883, 60)
threading.Thread(target=clientCams.loop_forever).start()

clientRsu = mqtt.Client()
clientRsu.on_connect = on_connectRsu
clientRsu.on_message = on_messageRsu
clientRsu.connect("192.168.98.1", 1883, 60)
threading.Thread(target=clientRsu.loop_forever).start()

clientLamps = mqtt.Client()
clientLamps.on_connect = on_connectLamps
clientLamps.on_message = on_messageLamps
clientLamps.connect("192.168.98.1", 1883, 60)
threading.Thread(target=clientLamps.loop_forever).start()


def main():
    print("Starting RSU1")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()