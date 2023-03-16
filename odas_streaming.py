import socket
import threading
import time
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from queue import Queue
from queue import Empty
import argparse
from pythonosc import udp_client
import speech_recognition as sr
import pyaudio
# import random


# Setup to live plot localisation (ssl) data
# x_data = []
# y_data = []


screen_mapping = -7.5
min_energy = 0.3            # Play around with this value - louder rooms need higher min energy (& vice versa)

eth_ip = "169.254.186.148"

osc_ip = "146.169.156.58"
osc_port = 7000
# FOR TESTING...
# osc_ip = "127.0.0.1"
# osc_port = 5005

# def animate(i):
#     plt.cla()
#     plt.title("Position Detected", fontsize = 25, fontname = "Helvetica")
#     plt.xlabel("X", fontsize=20, color="black", fontname = "Helvetica")
#     plt.ylabel("Y", fontsize = 20, color = "black", fontname = "Helvetica")	
#     plt.scatter(x_data, y_data, color="black")

def round_half_integer(number):
    """Round a number to the closest half integer.
    >>> round_off_rating(1.3)
    1.5
    >>> round_off_rating(2.6)
    2.5
    >>> round_off_rating(3.0)
    3.0
    >>> round_off_rating(4.1)
    4.0"""

    return round(number * 2) / 2

def init_tcp_server(port, type, x_queue):
    # Begin listening to socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((eth_ip, port))
    sock.listen()
    print(f"Listening for {type} connection")
    conn, addr = sock.accept()      # Waits until client connects
    with conn:
        print(f"Connected to {type}")
        while not die.is_set():
            data = conn.recv(4096)      # Receive data and do nothing
            if type == "ssl":
                try:
                    pos_dict = json.loads(data.decode('UTF-8'))     # Decode data into a dictionary
                except:
                    print("JSON recv failed")
                source1 = pos_dict["src"][0]
                energy1 = source1["E"]
                if energy1 > min_energy:
                    x1 = round_half_integer(source1["x"])*screen_mapping
                    print(x1)
                    x_queue.put(float(x1))
                    # print(round_half_integer(x1))
                    # y1 = source1["y"]
                    # z1 = source1["z"]
                    # x_data.append(x1)
                    # y_data.append(y1)
            if not data:
                break


# Setup OSC server to transmit positions to unity
def init_osc_client(ip_address, port, queue):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default=ip_address,
        help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=port,
        help="The port the OSC server is listening on")
    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.ip, args.port)
    print(f"OSC ready to send - IP: {ip_address}, Port: {port}")

    while not die.is_set():
        # queue.get() is blocking - the thread will hold until there is data in the queue
        queue_object = queue.get()
        # x_pos = float(random.randint(-7,7))       # For testing
        # Check if the data is a string (this will only come from voice commands)
        if isinstance(queue_object, str):
            # Then, send the data
            client.send_message("/voice_control", queue_object)
        else:
            # If not a string, will be a float - x position data
            client.send_message("/player/position", queue_object)


def init_mic_transcribe(msg_queue):
    # Initialise recogniser class
    init_rec = sr.Recognizer()

    # Use laptop microphone for sound source
    with sr.Microphone() as source:
        while True:
            try:
                # Pause to adjust energy level based on surrounding noise
                init_rec.adjust_for_ambient_noise(source, duration=0.2)
                
                audio_data = init_rec.record(source, duration=2)
                text = init_rec.recognize_google(audio_data)
                if "restart" in text:
                    msg_queue.put("restart")
                    print("restart")

            except sr.RequestError as e:
                pass
                # print("Could not request results; {0}".format(e))
            
            except sr.UnknownValueError:
                pass
                # print("unknown error occurred")
    



# Setup queue to share data between threads (and transmit over osc)
osc_queue = Queue()

# Setup multiple threads - one thread for each socket (4 separate servers, effectively)
die = threading.Event()
ssl_thread = threading.Thread(target=init_tcp_server, args=(9001, "ssl", osc_queue))
sst_thread = threading.Thread(target=init_tcp_server, args=(9000, "sst", osc_queue))
sss_sep_thread = threading.Thread(target=init_tcp_server, args=(10000, "sss", osc_queue))
sss_pf_thread = threading.Thread(target=init_tcp_server, args=(10010, "sss", osc_queue))
ssl_thread.start()
sst_thread.start()
sss_sep_thread.start()
sss_pf_thread.start()

osc_thread = threading.Thread(target=init_osc_client, args=(osc_ip, osc_port, osc_queue))
osc_thread.start()

transcribe_thread = threading.Thread(target=init_mic_transcribe, args=(osc_queue, ))
transcribe_thread.start()

# Start plotting the results...
# ani = animation.FuncAnimation(plt.gcf(), animate, interval=100)	
# plt.tight_layout()
# plt.show()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    die.set()
    plt.close()
    ssl_thread.join()
    sst_thread.join()
    sss_sep_thread.join()
    sss_pf_thread.join()
    osc_thread.join()
    transcribe_thread.join()