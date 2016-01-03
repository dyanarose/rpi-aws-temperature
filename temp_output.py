import boto3
import LCD1602
import time
import sys
import json

url = 'https://sqs.us-east-1.amazonaws.com/238322712540/rpi-test'
sqs = boto3.resource('sqs')

output = [lambda x: temp_out_console(x), lambda x: temp_out_LCD(x)]
queue = sqs.Queue(url)


def setup():
    LCD1602.init(0x27, 1)
    LCD1602.write(0, 0, 'Hello!')


def in_from_sqs():
    cur = ''
    while True:
        for message in queue.receive_messages():
            body = json.loads(message.body)
            if body and 'temperature' in body:
                temp = get_temp(body)
                if temp != cur:
                    cur = temp
                    for d in output:
                        d(cur)

            message.delete()

        time.sleep(30)


def get_temp(body):
    return body.get('temperature')


def temp_out_console(temp):
    print "Current temperature : " + temp + " C"


def temp_out_LCD(temp):
    LCD1602.clear()
    LCD1602.write(0, 0, 'current temp:')
    LCD1602.write(1, 1, temp + ' C')


def destroy():
    LCD1602.clear()


if __name__ == '__main__':
    try:
        setup()
        in_from_sqs()
    except KeyboardInterrupt:
        destroy()
    except:
        print "Unexpected Error " + sys.exc_info()[0]
        destroy()
