# Python file to make a mqtt publisher and subscriber
# The idea is to have a publisher that publishes a message when a given coordinate is reached 

import paho.mqtt.client as mqtt
import time
import json
import random
from geopy.distance import distance, geodesic
from geopy import Point
import math
from termcolor import colored
import threading

ID=1

def calculate_initial_compass_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    The formula used to calculate bearing is:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) - sin(lat1).cos(lat2).cos(Δlong))
    :param pointA: tuple of float (lat, long)
    :param pointB: tuple of float (lat, long)
    :returns: initial compass bearing in degrees, as a float
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2() returns values from -π to + π
    # So we need to normalize the result, to convert it to a compass bearing as it
    # should be in the range 0° to 360°
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def get_coordinates(lat1, lon1, lat2, lon2, speed):
    start = Point(latitude=lat1, longitude=lon1)
    end = Point(latitude=lat2, longitude=lon2)
    distance = geodesic(start, end).kilometers
    distance_meters = distance * 1000
    speedms = speed * 0.277778
    #how many seconds it takes to travel the distance_meters at speedms
    seconds = distance_meters / speedms
    #how many times the message should be sent per second
    N = 10
    #how many samples to take
    samples = int(seconds * N)
    #step size in meters
    step = distance_meters / samples

    bearing = calculate_initial_compass_bearing((lat1, lon1), (lat2, lon2))

    coordinates = []
    for i in range(samples+1):
        step_distance = step * i
        step_point = geodesic(meters=step_distance).destination(point=start, bearing=bearing)
        #round to only 6 decimal places after the point
        step_point.latitude = round(step_point.latitude, 6)
        step_point.longitude = round(step_point.longitude, 6)
        coordinates.append((step_point.latitude, step_point.longitude))

    return coordinates

def coordinates_to_dict(coordinates):
    return {i+1: (round(coordinate[0], 6), round(coordinate[1], 6)) for i, coordinate in enumerate(coordinates)}

def travel(street_list, speed_list, delay):
    j = 0
    for street in street_list:
        for key, coord in street.items():
            message = construct_message(coord[0], coord[1], speed_list[j])
            publish_message(message)
            print(colored("latitude: " + str(coord[0]) + " longitude: " + str(coord[1]) + " speed: " + str(speed_list[j]) +" km/h","green"))
            time.sleep(delay)
        j += 1
        print("\n")


client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
client.connect("192.168.98.11", 1883, 60)

threading.Thread(target=client.loop_forever).start()

# create a function that will publish the message to the broker mosquitto_pub -h 192.168.98.1 -t "vanetza/in/cam" -m "message"
def publish_message(message):
    client.publish("vanetza/in/cam", message)

def construct_message(latitude,longtitude, speed):
    global ID
    f = open('./in_cam.json')
    m = json.load(f)
    m["latitude"] = latitude
    m["longitude"] = longtitude
    m["speed"] = speed
    m["stationID"] = ID
    m = json.dumps(m)
    return m


#street = [(start.x, start.y), (end.x, end.y), speed in km/h]

av_25_abril_1 = [(40.638049, -8.649238), (40.636935, -8.647825), 55]
av_25_abril_2 = [(40.636935, -8.647825), (40.636039, -8.646736), 50]
av_25_abril_3 = [(40.636039, -8.646736), (40.634814, -8.645164), 55]
av_oita_1 = [(40.636731, -8.645732), (40.636039, -8.646736), 40]
av_oita_1_r = [(40.636039, -8.646736), (40.636731, -8.645732), 40]
av_oita_2 = [(40.636039, -8.646736), (40.635729, -8.647199), 45]
r_neves_1 = [(40.637832, -8.646591), (40.636935, -8.647825), 30]
r_neves_2 = [(40.636935, -8.647825), (40.636576, -8.648289), 30]
r_martinho_1 = [(40.635729, -8.647199), (40.636578, -8.648285), 30]
r_martinho_2 = [(40.636578, -8.648285), (40.637294, -8.649625), 30]
r_tv_martinho_1 = [(40.637294, -8.649625), (40.637514, -8.649407), 30]
r_tv_martinho_2 = [(40.637514, -8.649407), (40.637797, -8.649554), 30]
r_tv_martinho_3 = [(40.637797, -8.649554), (40.638049, -8.649238), 30]

av_25_abril_1_street = coordinates_to_dict(get_coordinates(av_25_abril_1[0][0], av_25_abril_1[0][1], av_25_abril_1[1][0], av_25_abril_1[1][1], av_25_abril_1[2]))
av_25_abril_2_street = coordinates_to_dict(get_coordinates(av_25_abril_2[0][0], av_25_abril_2[0][1], av_25_abril_2[1][0], av_25_abril_2[1][1], av_25_abril_2[2]))
av_25_abril_3_street = coordinates_to_dict(get_coordinates(av_25_abril_3[0][0], av_25_abril_3[0][1], av_25_abril_3[1][0], av_25_abril_3[1][1], av_25_abril_3[2]))
av_oita_1_street = coordinates_to_dict(get_coordinates(av_oita_1[0][0], av_oita_1[0][1], av_oita_1[1][0], av_oita_1[1][1], av_oita_1[2]))
av_oita_1_r_street = coordinates_to_dict(get_coordinates(av_oita_1_r[0][0], av_oita_1_r[0][1], av_oita_1_r[1][0], av_oita_1_r[1][1], av_oita_1_r[2]))
av_oita_2_street = coordinates_to_dict(get_coordinates(av_oita_2[0][0], av_oita_2[0][1], av_oita_2[1][0], av_oita_2[1][1], av_oita_2[2]))
r_neves_1_street = coordinates_to_dict(get_coordinates(r_neves_1[0][0], r_neves_1[0][1], r_neves_1[1][0], r_neves_1[1][1], r_neves_1[2]))
r_neves_2_street = coordinates_to_dict(get_coordinates(r_neves_2[0][0], r_neves_2[0][1], r_neves_2[1][0], r_neves_2[1][1], r_neves_2[2]))
r_martinho_1_street = coordinates_to_dict(get_coordinates(r_martinho_1[0][0], r_martinho_1[0][1], r_martinho_1[1][0], r_martinho_1[1][1], r_martinho_1[2]))
r_martinho_2_street = coordinates_to_dict(get_coordinates(r_martinho_2[0][0], r_martinho_2[0][1], r_martinho_2[1][0], r_martinho_2[1][1], r_martinho_2[2]))
r_tv_martinho_1_street = coordinates_to_dict(get_coordinates(r_tv_martinho_1[0][0], r_tv_martinho_1[0][1], r_tv_martinho_1[1][0], r_tv_martinho_1[1][1], r_tv_martinho_1[2]))
r_tv_martinho_2_street = coordinates_to_dict(get_coordinates(r_tv_martinho_2[0][0], r_tv_martinho_2[0][1], r_tv_martinho_2[1][0], r_tv_martinho_2[1][1], r_tv_martinho_2[2]))
r_tv_martinho_3_street = coordinates_to_dict(get_coordinates(r_tv_martinho_3[0][0], r_tv_martinho_3[0][1], r_tv_martinho_3[1][0], r_tv_martinho_3[1][1], r_tv_martinho_3[2]))

# create a main function that will run the program
def main():
    path = [av_25_abril_1_street, av_25_abril_2_street, av_oita_2_street,  r_martinho_1_street, r_martinho_2_street, \
            r_tv_martinho_1_street, r_tv_martinho_2_street, r_tv_martinho_3_street]
    speed = [55, 50, 45, 30, 30, 30, 30, 30]
    while True:
        #main street with average speed of 50km/h and resolution of 10Hz
        travel(path, speed, 0.1)
        # time.sleep(3)


if __name__ == "__main__":
    main()





