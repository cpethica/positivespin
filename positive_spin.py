"""
Combined OSC server and client to route messages locally
Detects machine IP and uses for server address. in/out ports are user defined.
Monitors specified OSC addresses.
"""

import argparse
import configparser
import random
import time
import math
import threading
from pathlib import Path

from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from threading import Thread

# variables to store incoming timeline values
timeline_1 = -1
timeline_2 = -1
timeline_3 = -1

# function flags
drum_flag_1 = False    # have buttons been pressed flags
drum_flag_2 = False
drum_flag_3 = False

drum_1_stop = True    # drum has slowed down fully after button press
drum_2_stop = True    # drum has slowed down fully after button press
drum_3_stop = True    # drum has slowed down fully after button press

startup = 0     # startup flag - game started (triggers drum speed up)

# address to monitor if selected
parser = argparse.ArgumentParser()
parser.add_argument("--monitor", type=str, default='/none')
args = parser.parse_args()

# get values from config file
p = Path(__file__).with_name('config.ini')
parser = configparser.ConfigParser()
parser.read(p)

for section_name in parser.sections():
    print('Section:', section_name)
    print('  Options:', parser.options(section_name))
    for name, value in parser.items(section_name):
        print('  %s = %s' % (name, value))
print()

# IP's and Ports
serverip = parser['IP_addresses']['server']
clientip = parser['IP_addresses']['client']
timelineport = parser.getint('OSC_ports', 'timeline')
buttonport = parser.getint('OSC_ports', 'buttons')
clientport = parser.getint('OSC_ports', 'out')

button_inputs = []   # read all osc button input addresses as list
for name in parser.options('button_inputs'):
    button_inputs.append(parser.get('button_inputs', name))
timeline_inputs = []   # read all osc timeline input addresses as list
for name in parser.options('timeline_inputs'):
    timeline_inputs.append(parser.get('timeline_inputs', name))

OSC_outputs = []  # read all osc input addresses as list
for name in parser.options('OSC_outputs'):
    OSC_outputs.append(parser.get('OSC_outputs', name))

# timers and delays
win_delay = parser.getint('delays', 'win_delay')
acceleration = parser.getfloat('drum_speed', 'acceleration')
deceleration = parser.getfloat('drum_speed', 'deceleration')
lag = parser.getint('drum_speed', 'lag')
fade = parser.getint('drum_speed', 'fade')
fps = parser.getint('drum_speed', 'fps')

# print some basic info then trigger other functions for drum slowdown, osc etc
def button_handler_1(unused_addr, *args):
    if timeline_1 != -1 and drum_flag_1 == False:
        drum_1(timeline_1)  # send timeline data to function to handle osc etc
        print(OSC_outputs[0] + str(timeline_1)) # prints address to send to and timeline value when pressed


def button_handler_2(address, *args):
    if timeline_2 != -1 and drum_flag_2 == False:
        print(OSC_outputs[1] + str(timeline_2))
        drum_2(timeline_2)  # send timeline data to function to handle osc etc


def button_handler_3(address, *args):
    if timeline_3 != -1 and drum_flag_3 == False:
        print(OSC_outputs[2] + str(timeline_3))
        drum_3(timeline_3)  # send timeline data to function to handle osc etc


# update timeline variables from incoming OSC messages
def timeline_handler_1(address, *args):
    global timeline_1
    timeline_1 = args[0]

def timeline_handler_2(address, *args):
    global timeline_2
    timeline_2 = args[0]

def timeline_handler_3(address, *args):
    global timeline_3
    timeline_3 = args[0]


if __name__ == "__main__":
    # listen to addresses and print changes in values
    dispatcher = Dispatcher()
    dispatcher.map(button_inputs[0], button_handler_1)
    dispatcher.map(button_inputs[1], button_handler_2)
    dispatcher.map(button_inputs[2], button_handler_3)
    dispatcher.map(timeline_inputs[0], timeline_handler_1)
    dispatcher.map(timeline_inputs[1], timeline_handler_2)
    dispatcher.map(timeline_inputs[2], timeline_handler_3)


def start_server(ip, port):

    print("Starting Server")
    server = osc_server.ThreadingOSCUDPServer(
        (ip, port), dispatcher)
    print("Serving on {}".format(server.server_address))
    thread = threading.Thread(target=server.serve_forever)
    thread.start()

def start_client(ip, port):
    global client
    print("Starting Client")
    client = udp_client.SimpleUDPClient(ip, port)

# Drum Functions:

reading = [-1,-1,-1]
# take time from button handler functions and use to send osc and set acceleration
def drum_1(press):
    client.send_message(OSC_outputs[0] + str(press)[2], '')
    global drum_flag_1
    drum_flag_1 = True      # set flag so we can work out when all buttons have been pressed
    reading[0] = int(str(press)[2])   # record card reading in array for when they've all been presses

def drum_2(press):
    client.send_message(OSC_outputs[1] + str(press)[2], '')
    global drum_flag_2
    drum_flag_2 = True      # set flag so we can work out when all buttons have been pressed
    reading[1] = int(str(press)[2])

def drum_3(press):
    client.send_message(OSC_outputs[2] + str(press)[2], '')
    global drum_flag_3
    drum_flag_3 = True      # set flag so we can work out when all buttons have been pressed
    reading[2] = int(str(press)[2])

# sets drum speeds from parameters in config file and time of button press
def drum_speed(drum_number, time):
    pass


# start server for timeline input
start_server(serverip, timelineport)
# start server for button input
start_server(serverip, buttonport)
# start osc output client
start_client(clientip, clientport)

# reset drum flags
def reset_flags():
    global drum_flag_1
    drum_flag_1 = False
    global drum_flag_2
    drum_flag_2 = False
    global drum_flag_3
    drum_flag_3 = False
    global drum_1_stop
    drum_1_stop = True
    global drum_2_stop
    drum_2_stop = True
    global drum_3_stop
    drum_3_stop = True

# functions to slow drums after buttons have been pressed
def drum_1_slow():
    i = 1
    while i > 0:
        client.send_message(OSC_outputs[5], i)  # send float value (0-1) for drum speed
        i = i - (1/(lag * fps))
        time.sleep(1/fps)


def drum_2_slow():
    i = 1
    while i > 0:
        client.send_message(OSC_outputs[6], i)  # send float value (0-1) for drum speed
        i = i - (1/(lag * fps))
        time.sleep(1/fps)

def drum_3_slow():
    i = 1
    while i > 0:
        client.send_message(OSC_outputs[7], i)  # send float value (0-1) for drum speed
        i = i - (1/(lag * fps))
        time.sleep(1/fps)

# run game
while True:
    # do slow start for drums
    if startup == 0:
        for i in range(lag*fps):
            client.send_message(OSC_outputs[5], i/(lag*fps-1))  # send float value (0-1) for drum speed
            client.send_message(OSC_outputs[6], i / (lag * fps - 1))  # send float value (0-1) for drum speed
            client.send_message(OSC_outputs[7], i / (lag * fps - 1))  # send float value (0-1) for drum speed
            time.sleep(1/fps)    # sleep for 1 frame
        startup = 1
    # slow down drums as the buttons are pressed - need to remove sleep here so other button presses are registered during slow down
    # start slowdown threads for drums
    thread1 = Thread(target=drum_1_slow)
    thread2 = Thread(target=drum_2_slow)
    thread3 = Thread(target=drum_3_slow)
    if drum_flag_1 and drum_1_stop:
        thread1.start()
        drum_1_stop = False         # stop thread starting repeatedly
    if drum_flag_2 and drum_2_stop:
        thread2.start()
        drum_2_stop = False
    if drum_flag_3 and drum_3_stop:
        thread3.start()
        drum_3_stop = False

    # check to see if all buttons have been pressed - and all drums have finished slowing down...
    while drum_flag_1 and drum_flag_2 and drum_flag_3:
        # wait for last drum to finish spinning
        time.sleep(lag)
        print("winner!!!!")
        # for now just sum all readings and send osc
        print(sum(reading))
        client.send_message(OSC_outputs[3] + str(sum(reading)), '')
        # sleep for a bit
        time.sleep(win_delay)
        # reset arduino buttons and madmapper with OSC message and start again
        client.send_message(OSC_outputs[4], '')
        # reset flags
        reset_flags()
        startup = 0


