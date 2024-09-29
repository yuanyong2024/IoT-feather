'''
from machine import Pin
import utime
from machine import UART

uart2 = UART(UART.UART2, 115200, 8, 0, 1, 0)

pinTable=[Pin.GPIO1,Pin.GPIO2,Pin.GPIO3,Pin.GPIO4,Pin.GPIO5,Pin.GPIO6,Pin.GPIO7,Pin.GPIO8,Pin.GPIO9,Pin.GPIO10,Pin.GPIO11,Pin.GPIO12,Pin.GPIO13,Pin.GPIO14,Pin.GPIO15,Pin.GPIO16,Pin.GPIO17,Pin.GPIO18,Pin.GPIO19,Pin.GPIO20]
'''

'''
@Author: Baron
@Date: 2020-04-24
@LastEditTime: 2020-04-24 17:06:08
@Description: example for module umqtt
@FilePath: example_mqtt_file.py
'''
from umqtt import MQTTClient
import utime
import log
import checkNet
from machine import Pin
from machine import I2C 

from usr.CM1103 import *


PROJECT_NAME = "QuecPython_MQTT_example"
PROJECT_VERSION = "1.0.0"

checknet = checkNet.CheckNetwork(PROJECT_NAME, PROJECT_VERSION)


log.basicConfig(level=log.INFO)
mqtt_log = log.getLogger("MQTT")


state = 0

def sub_cb(topic, msg):
    global state
    mqtt_log.info("Subscribe Recv: Topic={},Msg={}".format(topic.decode(), msg.decode()))
    state = 1


if __name__ == '__main__':
    
    analogSwitch = Pin(Pin.GPIO21,Pin.OUT,Pin.PULL_DISABLE,1)
    i2c_obj = I2C(I2C.I2C1, I2C.STANDARD_MODE)
    adc = CM1103(i2c_obj)
    adc.write_config(mode=MODE.CONTINIOUS,mux=MUX.MUX_A0_GND,pga=PGA.PGA_4096)
    print(adc.analogRead(A0))
    print(adc.analogRead(A0))
    print(adc.analogRead(A0))

    stagecode, subcode = checknet.wait_network_connected(30)
    if stagecode == 3 and subcode == 1:
        mqtt_log.info('Network connection successful!')


        c = MQTTClient("umqtt_client_yuanyong2024", "broker.emqx.io", 1883)
        #c = MQTTClient("tester1", "x116de01.ala.cn-hangzhou.emqxsl.cn", 8830)
        c.set_callback(sub_cb)

        c.connect()
        '''
        c.subscribe(b"/public/TEST/quecpython")
        mqtt_log.info("Connected to mq.tongxinmao.com, subscribed to /public/TEST/quecpython topic" )

        c.publish(b"/public/TEST/quecpython", b"my name is Quecpython!")
        mqtt_log.info("Publish topic: /public/TEST/quecpython, msg: my name is Quecpython")

        while True:
            c.wait_msg() 
            if state == 1:
                break
        '''
        repeat = 0
        while True:
            utime.sleep(2)
            c.publish(b"/public/TEST/quecpython", b"my name is Quecpython!")
            mqtt_log.info("Publish topic: /public/TEST/quecpython, msg: my name is Quecpython") 
            repeat+=1
            if repeat>=10:
                break

        c.disconnect()
    else:
        mqtt_log.info('Network connection failed! stagecode = {}, subcode = {}'.format(stagecode, subcode))
