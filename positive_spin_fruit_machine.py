"""
Combined OSC server and client to route messages locally
Detects machine IP and uses for server address. in/out ports are user defined.
Monitors specified OSC addresses.

Updated version of positive spin to start spins with button press
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


# store card values from pressed buttons to determine reading later
reading = [-1,-1,-1]

# function flags
# have buttons been pressed flags
drum_flag_1 = False
drum_flag_2 = False
drum_flag_3 = False

# reading sent flags (prevent multiple OSC messages)
sent_1 = True
sent_2 = True
sent_3 = True

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
reset_delay = parser.getint('delays', 'reset_delay')
jackpot_delay = parser.getint('delays', 'jackpot_delay')

# button handlers - when pressed these set flags and assign (randomly...) the card reading for each reel (5 cards per reel)
def button_handler_1(unused_addr, *args):
    global drum_flag_1
    if drum_flag_1 == False:
        drum_flag_1 = True  # set flag so we can work out when all buttons have been pressed
        reading[0] = random.randint(1, 5)  # reading is a random number between 1 and 5
        client.send_message(OSC_outputs[0] + str(reading[0]), '')

def button_handler_2(address, *args):
    global drum_flag_2
    if drum_flag_2 == False:
        drum_flag_2 = True  # set flag so we can work out when all buttons have been pressed
        reading[1] = random.randint(1, 5)  # reading is a random number between 1 and 5
        client.send_message(OSC_outputs[1] + str(reading[1]), '')

def button_handler_3(address, *args):
    global drum_flag_3
    if drum_flag_3 == False:
        drum_flag_3 = True  # set flag so we can work out when all buttons have been pressed
        reading[2] = random.randint(1, 5)  # reading is a random number between 1 and 5
        client.send_message(OSC_outputs[2] + str(reading[2]), '')


if __name__ == "__main__":
    # listen to addresses and print changes in values
    dispatcher = Dispatcher()
    dispatcher.map(button_inputs[0], button_handler_1)
    dispatcher.map(button_inputs[1], button_handler_2)
    dispatcher.map(button_inputs[2], button_handler_3)


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
    global sent_1
    sent_1 = True
    global sent_2
    sent_2 = True
    global sent_3
    sent_3 = True

# run game
while True:
    # check to see if all buttons have been pressed
    while drum_flag_1 and drum_flag_2 and drum_flag_3:
        # sleep for a bit after final button press
        time.sleep(win_delay)
        # check for jackpot - probability = 1/25 (5 ways to do this out of 125 possible outcomes)
        if reading[0] == reading[1] == reading [2]:
            print("Jackpot!")
            print(reading)
            client.send_message(OSC_outputs[3] + 'jackpot/' + str(reading[0]), '')    # send OSC message /jackpot and integer for winning number
            # sleep before reset
            time.sleep(jackpot_delay)
        # check for a pair - probability 8/25)
        elif reading[0] == reading[1] or reading[1] == reading[2] or reading[0] == reading[2]:
            print("Pair!")
            print(reading)
            # work out which cards are the same for osc output
            if reading[0] == reading[1]:
                card = reading[0]
            else:
                card = reading[2]
            client.send_message(OSC_outputs[3] + 'pair/' + str(card), '')
            # sleep before reset
            time.sleep(reset_delay)
        else:
            print("Nothing!")
            print(reading)
            client.send_message(OSC_outputs[3] + 'nothing', '')
            # sleep before reset
            time.sleep(reset_delay)
        # reset arduino buttons and madmapper with OSC message and start again
        client.send_message(OSC_outputs[4], '')
        print("reset")
        # reset flags
        reset_flags()

