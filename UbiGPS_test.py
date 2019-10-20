import time
import requests
import math
import serial

port = "/dev/ttyS0"

TOKEN = "BBFF-m4n4owKIz7YTv6RoUNKQODEVrMuLev"  # Put your TOKEN here
DEVICE_LABEL = "RaspberryPi"  # Put your device label here
VARIABLE_LABEL_1 = "GPS"  # Put your first variable label here



def build_payload(variable_1,data):

    if data[0:6] == "$GPRMC":
        sdata = data.split(",")
        if sdata[2] == 'V':
            print "no satellite data available"
            return
        print "---Parsing GPRMC---",
        time = sdata[1][0:2] + ":" + sdata[1][2:4] + ":" + sdata[1][4:6]
        lat = decode(sdata[3]) #latitude
        dirLat = sdata[4]      #latitude direction N/S
        lng = decode(sdata[5]) #longitute
        dirLng = sdata[6]      #longitude direction E/W

        if dirLat == 'S':
           lat = '-' + lat

        if dirLng == 'W':
           lng = '-' + lng

        print "%s , %s" % (lat,lng)

    payload = {variable_1: {"value": 1, "context": {"lat": lat, "lng": lng}}}

    return payload

def decode(coord):
    #Converts DDDMM.MMMMM > DD deg MM.MMMMM min
    x = coord.split(".")
    head = x[0]
    tail = x[1]
    deg = head[0:-2]
    min = head[-2:]
    minseg = min + tail
    minseg_int = int(minseg)
    minseg_quant = format((minseg_int/.60), '.0f')
    minseg_str = str(minseg_quant)
    return deg + "." + minseg_str

def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True


def main():
    print "Receiving GPS data"
    ser = serial.Serial(port, 9600)
    data = ser.readline()
    payload = build_payload(VARIABLE_LABEL_1,data)


    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")

while (True):
    main()
    time.sleep(1)
