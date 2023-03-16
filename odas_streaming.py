import socket
import threading
import time
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from queue import Queue
import argparse
from pythonosc import udp_client
# import random


# Setup to live plot localisation (ssl) data
# x_data = []
# y_data = []


screen_mapping = -7.5
min_energy = 0.3

eth_ip = "169.254.186.148"

osc_ip = "146.169.156.58"

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

def init_tcp_server(port, type, queue):
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
                    queue.put(float(x1))
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
        x_pos = queue.get()
        # x_pos = float(random.randint(-7,7))       # For testing
        # Then, send the data
        client.send_message("/player/position", x_pos)  
    


# Setup queue to share data between threads
x_pos_queue = Queue()

# Setup multiple threads - one thread for each socket (4 separate servers, effectively)
die = threading.Event()
ssl_thread = threading.Thread(target=init_tcp_server, args=(9001, "ssl", x_pos_queue))
sst_thread = threading.Thread(target=init_tcp_server, args=(9000, "sst", x_pos_queue))
sss_sep_thread = threading.Thread(target=init_tcp_server, args=(10000, "sss", x_pos_queue))
sss_pf_thread = threading.Thread(target=init_tcp_server, args=(10010, "sss", x_pos_queue))
ssl_thread.start()
sst_thread.start()
sss_sep_thread.start()
sss_pf_thread.start()
osc_thread = threading.Thread(target=init_osc_client, args=(osc_ip, 7000, x_pos_queue))
# osc_thread = threading.Thread(target=init_osc_client, args=("127.0.0.1", 5005, x_pos_queue))
osc_thread.start()

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