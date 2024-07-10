"""
Combined OSC server and client to route messages locally
Detects machine IP and uses for server address. in/out ports are user defined.
Monitors specified OSC addresses.
"""

import argparse
import random
import math
import threading
import os
import socket
import signal
from tkinter import *

from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

# variable to store vezer timeline values
vezer_timeline_1 = -1
vezer_timeline_2 = -1
vezer_timeline_3 = -1


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


def button_handler_1(address, *args):
    card = str(vezer_timeline_1)
    print(card[2])
    client.send_message("/card1/", card[2])


def button_handler_2(address, *args):
    card = str(vezer_timeline_2)
    print(card[2])
    client.send_message("/card2/", card[2])


def button_handler_2(address, *args):
    card = str(vezer_timeline_3)
    print(card[2])
    client.send_message("/card3/", card[2])


def vezer_handler_1(address, *args):
    global vezer_timeline_1
    vezer_timeline_1 = args[0]

def vezer_handler_2(address, *args):
    global vezer_timeline_2
    vezer_timeline_2 = args[0]


def vezer_handler_3(address, *args):
    global vezer_timeline_3
    vezer_timeline_3 = args[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serverip", default=get_ip(), help="The ip to listen on")
    parser.add_argument("--serverport", type=int, default=9999, help="The port the OSC Server is listening on")
    parser.add_argument("--clientip", default="127.0.0.1", help="The ip of the OSC server")
    parser.add_argument("--clientport", type=int, default=8500, help="The port the OSC Client is listening on")
    args = parser.parse_args()

    # listen to addresses and print changes in values
    dispatcher = Dispatcher()
    dispatcher.map("/button1", button_handler_1)
    dispatcher.map("/timeline1", vezer_handler_1)
    dispatcher.map("/timeline2", vezer_handler_2)
    dispatcher.map("/timeline3", vezer_handler_3)



def shutdown():
    os.kill(os.getpid(), signal.SIGINT)


def clear():
    txt1.delete(0, END)
    textarea.config(state=NORMAL)
    textarea.delete('1.0', END)
    textarea.config(state=DISABLED)


def monitor_handler(address, *args):
    # check if there is data or only an address to display on the monitor
    if len(args) > 0:
        message = str(args[0])
    else:
        message = address
    textarea.config(state=NORMAL)
    textarea.insert(END, message + '\n')
    textarea.see(END)
    textarea.config(state=DISABLED)


# setup unused address to allow clearing of monitor below, then map to prevent error below...
previous_address = "/null"
dispatcher.map(previous_address, monitor_handler)

def monitor():
    global previous_address
    message = txt1.get()
    # unmap previously monitored address
    dispatcher.unmap(previous_address, monitor_handler)
    dispatcher.map(message, monitor_handler)
    previous_address = message

# start server with machine IP and port provided
def inport():
    start_server(get_ip(), int(txt2.get()))


def outport():
    start_client(get_ip(), int(txt3.get()))



root = Tk()


root.title('OSC Router/Monitor')
root.geometry('400x450')

lbl1 = Label(text='Monitor OSC address')
lbl1.place(x=0, y=0, width=200, height=50)

txt1 = Entry()
txt1.place(x=200, y=0, width=200, height=50)

btn1 = Button(text='Clear', command=clear)
btn1.place(x=0, y=50, width=200, height=50)

btn2 = Button(text='Monitor', command=monitor)
btn2.place(x=200, y=50, width=200, height=50)

btn3 = Button(text='Exit', command=shutdown)
btn3.place(x=0, y=100, width=200, height=50)

lbl4 = Label(text='Server/Client IP: '+get_ip())
lbl4.place(x=0, y=300, width=200, height=50)

lbl5 = Label(text='Enter input port')
lbl5.place(x=0, y=350, width=125, height=50)

txt2 = Entry()
txt2.place(x=150, y=350, width=100, height=50)

btn4 = Button(text='Submit', command=inport)
btn4.place(x=300, y=350, width=100, height=50)

lbl6 = Label(text='Enter output port')
lbl6.place(x=0, y=400, width=125, height=50)

txt3 = Entry()
txt3.place(x=150, y=400, width=100, height=50)

btn5 = Button(text='Submit', command=outport)
btn5.place(x=300, y=400, width=100, height=50)

textarea = Text(root, bg='white')
vscroll = Scrollbar(orient=VERTICAL)
vscroll.config(command=textarea.yview)
textarea.config(yscrollcommand=vscroll.set)
textarea.config(state=DISABLED)
textarea.place(x=0, y=150, width=380, height=150)
vscroll.place(x=380, y=150, width=20, height=150)
root.mainloop()
