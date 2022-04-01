import random
import threading
import socket
from StateEnum import State
import time


class Node(threading.Thread):

    def __init__(self, id, port, request_delay_time_upper, critical_section_time_upper):
        super(Node, self).__init__(daemon=False)

        self.id = id
        self.host = '127.0.0.1'
        self.port = port
        self.state = State.DO_NOT_WANT
        self.request_delay_time_upper = request_delay_time_upper
        self.critical_section_time_upper = critical_section_time_upper
        self.request_timestamp = None

        self.delay_start_timestamp = 0
        self.delay = 0
        self.queue = set()

        self.nodes_to_connect = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()

    def init_server(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(1)
        self.sock.listen()

    def collect_node_port(self, port):
        self.nodes_to_connect[port] = "NOK"

    def send_request(self, port, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, port))
        sock.send((str(message) + '|' + str(self.port)).encode('utf-8'))

    def response_processing(self, node_time, node_port):
        if self.state == State.DO_NOT_WANT:
            self.send_request(node_port, 'OK')
        elif self.state == State.HELD:
            self.queue.add(node_port)
        else:
            if self.request_timestamp < node_time:
                self.queue.add(node_port)
            elif self.request_timestamp > node_time:
                self.send_request(node_port, 'OK')
            else:
                self.send_request(node_port, 'OK')

    def request_processing(self, message):
        node_message, node_port = message.split('|')
        if node_message == 'OK':
            self.nodes_to_connect[int(node_port)] = "OK"
        else:
            self.response_processing(float(node_message), int(node_port))

    def get_request(self):
        try:
            connection, client_address = self.sock.accept()
            message = connection.recv(4096).decode('utf-8')
            self.request_processing(message)
        except socket.timeout:
            pass

    def check_access(self):
        total = len(self.nodes_to_connect)
        count_ok = len([1 for value in self.nodes_to_connect.values() if value == 'OK'])
        if total == count_ok:
            self.state = State.HELD

    def run(self):
        delay_start_timestamp = None
        delay_started = False
        while True:

            # handle incoming requests
            self.get_request()

            if self.state == State.HELD:
                if not delay_started:
                    delay_start_timestamp = time.time()
                    self.delay = random.randint(10, self.critical_section_time_upper)
                    delay_started = True
                elif delay_started and time.time() - delay_start_timestamp >= self.delay:
                    self.state = State.DO_NOT_WANT
                    delay_started = False
                    for node_port in self.queue:
                        self.send_request(node_port, 'OK')
                    for node_port in self.nodes_to_connect.keys():
                        self.collect_node_port(node_port)

            elif self.state == State.DO_NOT_WANT:
                if not delay_started:
                    delay_start_timestamp = time.time()
                    self.delay = random.randint(5, self.request_delay_time_upper)
                    delay_started = True
                else:
                    if time.time() - delay_start_timestamp >= self.delay:
                        self.state = State.WANTED
                        self.request_timestamp = time.time()
                        self.request_access()
                        delay_started = False

            # check if process can access CS
            else:  # self.state == State.WANTED:
                self.check_access()

    def request_access(self):
        for node_port in self.nodes_to_connect.keys():
            self.send_request(node_port, time.time())


def list_nodes(nodes):
    for node in nodes:
        print(f"P{node.id}, {node.state.value}, {node.request_timestamp}, {node.delay}")


def update_upper_delay(t, nodes):
    for node in nodes:
        node.request_delay_time_upper = t


def update_upper_cs(t, nodes):
    for node in nodes:
        node.critical_section_time_upper = t


def execute_command(input_command, nodes):
    cmd = input_command.lower().split()
    if cmd == "":
        print("Command not found")
        return True

    command = cmd[0]

    if command == 'list':
        try:
            list_nodes(nodes)
        except:
            print("Error")

    elif command == 'time-p':
        try:
            update_upper_delay(int(cmd[1]), nodes)
        except:
            print("Error")

    elif command == 'time-cs':
        try:
            update_upper_cs(int(cmd[1]), nodes)
        except:
            print("Error")

    elif command == 'exit':
        return False

    else:
        print("Command not found")

    return True


if __name__ == "__main__":
    N = 7
    nodes = []
    for i in range(N):
        node = Node(i + 1, 8000 + i, 10, 10)
        node.start()
        nodes.append(node)

    # save ports of other nodes in memory
    for node_host in nodes:
        for node_client in nodes:
            if node_host.id != node_client.id:
                node_host.collect_node_port(node_client.port)

    running = True
    while running:
        command = input("Command: ")
        running = execute_command(command, nodes)
