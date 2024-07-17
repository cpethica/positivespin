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

serverip = parser['IP_addresses']['main']
clientip = parser['IP_addresses']['main']
serverport = parser.getint('OSC_ports', 'in')
clientport = parser.getint('OSC_ports', 'out')

button_inputs = []   # read all osc button input addresses as list
for name in parser.options('button_inputs'):
    button_inputs.append(parser.get('button_inputs', name))
print(button_inputs[0])
timeline_inputs = []   # read all osc timeline input addresses as list
for name in parser.options('timeline_inputs'):
    timeline_inputs.append(parser.get('timeline_inputs', name))

OSC_outputs = []  # read all osc input addresses as list
for name in parser.options('OSC_outputs'):
    OSC_outputs.append(parser.get('OSC_outputs', name))

def button_handler_1(address, *args):
    print(OSC_outputs[0] + str(timeline_1)[2])
    client.send_message(OSC_outputs[0] + str(timeline_1)[2])


def button_handler_2(address, *args):
    print(OSC_outputs[1] + str(timeline_2)[2])
    client.send_message(OSC_outputs[1] + str(timeline_2)[2])


def button_handler_3(address, *args):
    print(OSC_outputs[2] + str(timeline_3)[2])
    client.send_message(OSC_outputs[2] + str(timeline_3)[2])


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
    dispatcher.map(args.monitor, print)
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


start_server(serverip, serverport)
start_client(clientip, clientport)
