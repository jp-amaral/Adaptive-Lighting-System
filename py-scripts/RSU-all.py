import paho.mqtt.client as mqtt
import time
from datetime import datetime
import json
import sys
from geopy.distance import distance
from termcolor import colored
import math as Math
import threading

class post:
    def __init__(self, x, y):
        self.x = x
        self.y = y

#make sure the program is called with the correct number of arguments (6)
if len(sys.argv) != 7:
    print("Usage: python3 RSU.py <ID> <latitude> <longitude> <bias> <IP> <POST_RANGE (meters)>")
    sys.exit(1)

#assign the arguments to variables
ID = int(sys.argv[1])
print(colored("ID: ", "magenta"), colored(ID, "magenta"))
post.x = float(sys.argv[2])
print(colored("post.x: ", "magenta"), colored(post.x, "magenta"))
post.y = -float(sys.argv[3])
print(colored("post.y: ", "magenta"), colored(post.y, "magenta"))
BIAS = float(sys.argv[4])
print(colored("BIAS: ", "magenta"), colored(BIAS, "magenta"))
IP = sys.argv[5]
print(colored("IP: ", "magenta"), colored(IP, "magenta"))
POST_RANGE = int(sys.argv[6])
print(colored("POST_RANGE: ", "magenta"), colored(POST_RANGE, "magenta"))
post = post(post.x, post.y)
LAMPS = {}

MY_STATUS = "dimmed"
MY_INTENSITY = 20
RADIUS = 100
IN_RANGE = False
ORDERING_RSU_ID = None
OBUS = {}
IN_RANGES = {}


last_3_distances = []

def on_connectLamps(client, userdata, flags, rc):
    print(colored("Connected with result code: ", "green"), colored(str(rc), "green"))
    client.subscribe("posts_info")

def on_messageLamps(client, userdata, msg):
    global LAMPS
    message = json.loads(msg.payload)
    LAMPS = message

def on_connectObu(client, userdata, flags, rc):
    print(colored("Connected with result code: ", "green"), colored(str(rc), "green"))
    client.subscribe("vanetza/out/cam")

def on_connectRsu(client, userdata, flags, rc):
    print(colored("Connected with result code: ", "green"), colored(str(rc), "green"))
    client.subscribe("all/lsm")


def on_messageRsu(client, userdata, msg):
    global MY_STATUS, MY_INTENSITY, BIAS, ORDERING_RSU_ID, last_3_distances
    message = json.loads(msg.payload)
    if(message["station_id"] == ID):
        return
    ORDERING_RSU_ID = -1
    dest_stations = message["dest_stations"]
    for key, value in dest_stations.items():
        if key == str(ID):
            # if MY_INTENSITY < value:
            MY_INTENSITY = value
            ORDERING_RSU_ID = message["station_id"]
            # print(colored("Intensity received: ", "yellow"), colored(MY_INTENSITY, "yellow"))

def on_messageObu(client, userdata, msg):
    global MY_STATUS, MY_INTENSITY, BIAS, IN_RANGE, OBUS, IN_RANGES
    #message info
    message = json.loads(msg.payload)
    longitude = message["longitude"]
    latitude = message["latitude"]
    speed = message["speed"]
    obu_id = message["stationID"]

    #check if this obu is in range and save it in the dictionary
    distance_between_car_and_post = round(distance((latitude, longitude), (post.x, post.y)).meters,2)
    if(distance_between_car_and_post > RADIUS):
        #check if in the previous iteration it was in range
        if(obu_id in IN_RANGES):
            if IN_RANGES[obu_id] == True:
                #last iteration it was in range, so it just left
                OBUS[obu_id]["longitude"] = -1
                OBUS[obu_id]["latitude"] = -1
                OBUS[obu_id]["speed"] = -1
                times = get_times_to_arrival(False)
                intensities = get_intensities(times, False, BIAS)
                out_message = construct_message([2], MY_INTENSITY, intensities, latitude, longitude, obu_id)
                publish_lsm(out_message)
        IN_RANGES[obu_id] = False
    else:
        IN_RANGES[obu_id] = True

    #stop processing if there are no obus in range and set IN_RANGE to false
    if not any(IN_RANGES.values()):
        IN_RANGE = False
        return
    else:
        IN_RANGE = True

    if(distance_between_car_and_post > RADIUS):
        print(colored("Distance is: ", "red"), colored(distance_between_car_and_post, "red"))
        return

    if(obu_id not in OBUS):
        OBUS[obu_id] = {"longitude": longitude, "latitude": latitude, "speed": speed}
        return
    else:
        OBUS[obu_id]["longitude"] = longitude
        OBUS[obu_id]["latitude"] = latitude
        OBUS[obu_id]["speed"] = speed

    #out of all the obus, get the closest distance
    closest_distance, closest_obu = get_closest_obu(OBUS, post.x, post.y)


    # last_3_distances.append(closest_distance)
    # if len(last_3_distances) > 3:
    #     last_3_distances.pop(0)

    facing = facing_post(last_3_distances)
    # print(facing)

    

    # if(MY_STATUS == "on"):
    #     print(colored("My status: ", "green"), colored(MY_STATUS, "green"))
    # else:
    #     print(colored("My status: ", "red"), colored(MY_STATUS, "red"))

    time_to_arrival = [round(calc_interval(closest_distance, speed),2)]
    iluminacao = calc_iluminacao(closest_distance,speed, BIAS, facing)
    MY_INTENSITY = iluminacao
    # print(colored("Time to arrival: ", "green"), time_to_arrival)
    # print(colored("Distance between car and post: ","blue"), closest_distance)
    # print(colored("Speed: ", "blue"), speed)
    # print(colored("Iluminacao: ", "yellow"), colored(iluminacao, "yellow"))  
    # print("\n")

    
    times = get_times_to_arrival(True)
    intensities = get_intensities(times, facing, BIAS)
    out_message = construct_message([2], MY_INTENSITY, intensities, latitude, longitude, obu_id)
    publish_lsm(out_message)
    
def publish_lsm(message):
    clientRsu.publish("all/lsm", message) #lsm = light support message
    # print(message)
    print("LSM published on all/lsm")

def publish_status(intensity, in_range, ordering_rsu_id):
    if in_range:
        ordering_rsu_id = ID
    message = {
        "station_id": ID,
        "intensity": intensity,
        "in_range": in_range,
        "ordering_rsu_id": ordering_rsu_id
    }
    clientRsu.publish("all/status", json.dumps(message))


def calc_iluminacao(distance, speed, bias, facing_post):
    global HIGHWAY
    tempo = calc_interval(distance, speed)
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

def construct_message(destination, intensity, intensities, latitude, longitude, obu_id):
    f = open('./out_lsm.json')
    m = json.load(f)
    m["dest_stations"] = intensities
    m["intensity"] = intensity
    m["station_id"] = ID
    m["station_latitude"] = post.x
    m["station_longitude"] = post.y
    m["obu_latitude"] = latitude
    m["obu_longitude"] = longitude
    m["obu_id"] = obu_id
    now = datetime.now()
    m["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S:%f")
    m = json.dumps(m)
    return m

# def get_post_ids():
#     global LAMPS
#     ids = []
#     for key, value in LAMPS.items():
#         lat = value['latitude']
#         lon = value['longitude']
#         difference_between_posts = round(distance((lat, lon), (post.x, post.y)).meters,2)
#         if difference_between_posts < RADIUS*1.8:
#             ids.append(key)
#     return ids

def get_times_to_arrival(in_range):
    global LAMPS, OBUS, RADIUS, POST_RANGE
    #for all the LAMPS, calculate the time to arrival of the closest obu
    times = {}
    for key, value in LAMPS.items():
        lat = value['latitude']
        lon = value['longitude']
        distance_val, obu_id = get_closest_obu(OBUS, lat, lon)
        difference_between_posts = round(distance((lat, lon), (post.x, post.y)).meters,2)
        if difference_between_posts < POST_RANGE:
            if(in_range):
                time_to_arrival = round(calc_interval(distance_val, OBUS[obu_id]["speed"]),2)
                times[key] = time_to_arrival
            else:
                times[key] = -1
    # print(times)
    return times

def intensity_on_time(tempo, facing, bias):
    if tempo == -1 or tempo == 0:
        return -1
    luminosidade = 1/tempo*100*bias

    if luminosidade > 100:
        luminosidade = 100

    if luminosidade <20:
        luminosidade = 20
    
    return Math.ceil(luminosidade)


def get_intensities(times, facing, bias):
    intensities = {}
    for key, value in times.items():
        temp = intensity_on_time(value, facing,  bias)
        if (temp > 20):
            intensities[key] = temp
        elif (value == -1):
            intensities[key] = -1
        # intensities[key] = intensity_on_time(value, bias)

    return intensities

def get_closest_obu(OBUS, post_lat, post_long):
    closest_distance = 100000
    closest_obu = -1
    for key, value in OBUS.items():
        obu_lat = value['latitude']
        obu_long = value['longitude']
        if obu_lat == -1 and obu_long == -1:
            continue
        distance_between_car_and_post = round(distance((obu_lat, obu_long), (post_lat, post_long)).meters,2)
        if distance_between_car_and_post < closest_distance:
            closest_distance = distance_between_car_and_post
            closest_obu = key
    return closest_distance, closest_obu



clientObu = mqtt.Client()
clientObu.on_connect = on_connectObu
clientObu.on_message = on_messageObu
clientObu.connect(IP, 1883, 60)
threading.Thread(target=clientObu.loop_forever).start()

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
    time.sleep(0.5)
    print("Starting RSU"+str(ID)+"...")
    while True:
        publish_status(MY_INTENSITY, IN_RANGE, ORDERING_RSU_ID)
        time.sleep(0.2)

if __name__ == "__main__":
    main()