
from pythonosc import udp_client

import time
import keyboard
from pathlib import Path
import configparser

# get values from config file
p = Path(__file__).with_name('config.ini')
parser = configparser.ConfigParser()
parser.read(p)

button_inputs = []   # read all osc button input addresses as list
for name in parser.options('button_inputs'):
    button_inputs.append(parser.get('button_inputs', name))

clientip = parser['IP_addresses']['client']
clientport = parser.getint('OSC_ports', 'buttons')

def start_client(ip, port):
    global client
    print("Starting Client")
    client = udp_client.SimpleUDPClient(ip, port)

start_client(clientip, 5000)

while True:
    if keyboard.is_pressed("1"):
        print("You pressed '1'.")
        client.send_message(button_inputs[0], '')
        time.sleep(0.1)
    if keyboard.is_pressed("2"):
        print("You pressed '2'.")
        client.send_message(button_inputs[1], '')
        time.sleep(0.1)
    if keyboard.is_pressed("3"):
        print("You pressed '3'.")
        client.send_message(button_inputs[2], '')
        time.sleep(0.1)
