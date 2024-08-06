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

# variables to store incoming timeline values
timeline_1 = -1
timeline_2 = -1
timeline_3 = -1

# button pressed flags
drum_flag_1 = False
drum_flag_2 = False
drum_flag_3 = False

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

# print some basic info then trigger other functions for drum slowdown, osc etc
def button_handler_1(unused_addr, *args):
    if (timeline_1 != -1):
        drum_1(timeline_1)  # send timeline data to function to handle osc etc
        print(OSC_outputs[0] + str(timeline_1)) # prints address to send to and timeline value when pressed
    else:
        print("No OSC "+OSC_outputs[0]+" timeline data received")

def button_handler_2(address, *args):
    if (timeline_2 != -1):
        print(OSC_outputs[1] + str(timeline_2))
        drum_2(timeline_2)  # send timeline data to function to handle osc etc
    else:
        print("No OSC "+OSC_outputs[1]+" timeline data received")

def button_handler_3(address, *args):
    if (timeline_3 != -1):
        print(OSC_outputs[2] + str(timeline_3))
        drum_3(timeline_3)  # send timeline data to function to handle osc etc
    else:
        print("No OSC "+OSC_outputs[2]+" timeline data received")

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

# take time from button handler functions and use to send osc and set acceleration
def drum_1(press):
    client.send_message(OSC_outputs[0] + str(press)[2], '')
    global drum_flag_1
    drum_flag_1 = True      # set flag so we can work out when all buttons have been pressed

def drum_2(press):
    client.send_message(OSC_outputs[1] + str(press)[2], '')
    global drum_flag_2
    drum_flag_2 = True      # set flag so we can work out when all buttons have been pressed

def drum_3(press):
    client.send_message(OSC_outputs[2] + str(press)[2], '')
    global drum_flag_3
    drum_flag_3 = True      # set flag so we can work out when all buttons have been pressed


# sets drum speeds from parameters in config file and time of button press
def drum_speed(drumber, time):
    pass

# do something when all buttons have been pressed
def winner():
    global drum_flag_1, drum_flag_2, drum_flag_3
    while drum_flag_1 and drum_flag_2 and drum_flag_3:
        print("winner!!!!")
        # reset flags
        drum_flag_1 = False
        drum_flag_2 = False
        drum_flag_3 = False

# start server for timeline input
start_server(serverip, timelineport)
# start server for button input
start_server(serverip, buttonport)
# start osc output client
start_client(clientip, clientport)

# run game
while True:
    winner()