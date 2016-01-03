#!/usr/bin/env python
import time
import sys
import requests
import json


ds18b20 = '28-0315043fb7ff'
baseurl = 'https://w91dz3u110.execute-api.us-east-1.amazonaws.com'
url = baseurl + '/prod/tempRecorder'


output = [lambda x: temp_out_console(x), lambda x: temp_out_aws(x)]


def read(text):
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    temperature = temperature / 1000
    return temperature


def loop():
    cur = ''
    location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave'
    with open(location) as tfile:
        while True:
            time.sleep(10)
            text = tfile.read()
            tfile.seek(0)
            temp = read(text)
            if temp:
                ftemp = "%0.3f" % temp
                if cur != ftemp:
                    cur = ftemp
                    for o in output:
                        o(temp)


def temp_out_console(temp):
    print "Current temperature : " + "%0.3f" % temp + " C"


def temp_out_aws(temp):
    payload = convert_to_payload(temp)
    result = requests.post(url, data=json.dumps(payload))
    if result.status_code != 200:
        print(result.status_code)
        print(result.text)


def convert_to_payload(temp):
    return {'temperature': "%0.3f" % temp,
            'time': int(time.time()),
            'device': 'desktop pi'}


def destroy():
    pass

if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
    except:
        print "Unexpected Error" + sys.exc_info()[0]
        destroy()
