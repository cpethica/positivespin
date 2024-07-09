"""Small example OSC server anbd client combined
This program listens to serveral addresses and print if there is an input.
It also transmits on a different port at the same time random values to different addresses.
This can be used to demonstrate concurrent send and recieve over OSC
"""

# TO DO!!!!
#
# query system for IP then use as default for server below
#
#


import argparse
import random
import time
import math
import threading

from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

import socket

# variable to store vezer timeline values
vezer_timeline_1 = -1
vezer_timeline_2 = -1
vezer_timeline_3 = -1

# find machines IP address for use as default for OSC server
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def button_handler(str, *args):
    print(vezer_timeline_1)
    print(vezer_timeline_2)


def vezer_handler_1(str, *args):
    global vezer_timeline_1
    vezer_timeline_1 = args[0]

def vezer_handler_2(str, *args):
    global vezer_timeline_2
    vezer_timeline_2 = args[0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serverip", default=get_ip(), help="The ip to listen on")
    parser.add_argument("--serverport", type=int, default=9999, help="The port the OSC Server is listening on")
    parser.add_argument("--clientip", default="127.0.0.1", help="The ip of the OSC server")
    parser.add_argument("--clientport", type=int, default=8500, help="The port the OSC Client is listening on")
    args = parser.parse_args()


    # listen to addresses and print changes in values
    dispatcher = Dispatcher()
    dispatcher.map("/button1", button_handler)
    dispatcher.map("/timeline_1", vezer_handler_1)
    dispatcher.map("/timeline_2", vezer_handler_2)

def start_server(ip, port):

    print("Starting Server")
    server = osc_server.ThreadingOSCUDPServer(
        (ip, port), dispatcher)
    print("Serving on {}".format(server.server_address))
    thread = threading.Thread(target=server.serve_forever)
    thread.start()

# def start_client(ip, port):
#     print("Starting Client")
#     client = udp_client.SimpleUDPClient(ip, port)
#     # print("Sending on {}".format(client.))
#     thread = threading.Thread(target=random_values(client))
#     thread.start()




start_server(args.serverip, args.serverport)
# start_client(args.clientip, args.clientport)