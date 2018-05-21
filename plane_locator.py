import requests
import json
from opensky_api import OpenSkyApi
import geopy
import geopy.distance
import numpy

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_current_location():
    send_url = 'http://api.ipstack.com/46.183.103.17?access_key=42f1ed0e07b98b7784f32914f657aea9'
    r = requests.get(send_url)
    j = json.loads(r.text)
    lat = j['latitude']
    lon = j['longitude']
    continent = j['continent_name']
    country = j['country_name']
    city = j['city']
    zip = j['zip']
    print("-" * 30)
    print("Your " + bcolors.WARNING + "Current " + bcolors.ENDC + "location")
    print("\nContinent: " + bcolors.FAIL + str(continent) + bcolors.ENDC +
           "\nCountry: " + bcolors.HEADER + str(country) + bcolors.ENDC +
           "\nCity: " + bcolors.OKBLUE + str(city) + bcolors.ENDC +
           "\nZip Code: " + bcolors.OKGREEN + str(zip) + bcolors.ENDC +
           "\nLatitude: " + bcolors.WARNING + str(lat)  + bcolors.ENDC +
           "\nLongitude: " + bcolors.WARNING + str(lon)  + bcolors.ENDC)
    print(("-" * 30) + "\n")
    return [lat, lon] #latitude by longitude


def calculate_bouding_box(lat, lon, distance): #Rough estimation because calculation will be done as a circle but limited to bouding box inside
    print("\nArea being calculated")
    start = geopy.Point(lat,lon)
    d = geopy.distance.VincentyDistance(kilometers=distance)
    print("Please wait...")
    top_right = d.destination(point=start, bearing=45)
    bottom_left = d.destination(point=start, bearing=225)
    print("Done Calculating")
    return [bottom_left.latitude, top_right.latitude, bottom_left.longitude, top_right.longitude] #min latitude, max latitude, min longitude, max longitude


def find_current_planes(bounding_box, current_location):
    print("\nFinding planes within distance")
    api = OpenSkyApi()

    # bbox = (min latitude, max latitude, min longitude, max longitude)
    states = api.get_states(bbox=(bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3]))
    print("Please wait...")
    for s in states.states:
        a = numpy.array((current_location[0], current_location[1], 0))
        height = s.baro_altitude
        if height == None:
            height = 0
        b = numpy.array((s.latitude, s.longitude, height))
        distance = numpy.linalg.norm(a-b)
        print(("\nCallsign: " + bcolors.FAIL + "%r" + bcolors.ENDC +
              "\nOrigin Country: " + bcolors.HEADER + "%r" + bcolors.ENDC +
              "\nLongitude: " + bcolors.OKBLUE + "%r" + bcolors.ENDC +
              "\nLatidue: " + bcolors.OKGREEN + "%r" + bcolors.ENDC +
              "\nVelocity: " + bcolors.WARNING + "%r" + "m/s" + bcolors.ENDC +
              "\nAltitude: " + bcolors.WARNING + "%r" + " meters" + bcolors.ENDC +
              "\nDistance from you: " + bcolors.FAIL +  str(distance) + bcolors.ENDC + " meters" +
              "\nOn Ground: " + bcolors.ENDC + "%r" + bcolors.ENDC) % (s.callsign, s.origin_country, s.longitude, s.latitude, s.velocity, s.baro_altitude, s.on_ground))
    print("Planes found")


def main():
    current_location = get_current_location()
    distance = int(input("How many kilometers away would you like to check for planes?\n: "))
    bounding_box = calculate_bouding_box(current_location[0], current_location[1], distance)

    find_current_planes(bounding_box, current_location)


if __name__ == "__main__":
    main()
