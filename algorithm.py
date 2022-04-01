import socket
import threading

import rpyc
from rpyc.utils.server import ThreadedServer
import datetime
import _thread
import time
import enum
import random

processes = []


class State(enum.Enum):
    HELD = 'HELD'
    WANTED = 'WANTED'
    DO_NOT_WANT = 'DO-NOT-WANT'


class CriticalSection:

    def give_access(self, process):
        _thread.start_new_thread(self.run, (process, ))

    def run(self, process):
        process.state = State.HELD
        time.sleep(random.randint(10, process.critical_section_time_upper))
        process.state = State.DO_NOT_WANT

class Process:
    def __init__(self, id, state, request_delay_time_upper, critical_section_time_upper):
        self.id = id
        self.state = state
        self.request_delay_time_upper = request_delay_time_upper
        self.critical_section_time_upper = critical_section_time_upper
        self.request_timestamp = None

    def start(self):
        _thread.start_new_thread(self.run, ())

    def run(self):
        while True:
            delay = random.randint(5, self.request_delay_time_upper)
            time.sleep(delay)
            if self.state == State.DO_NOT_WANT:
                self.state = State.WANTED
                self.request_timestamp = time.time()
                self.request_access(processes)

    def request_access(self, processes):
        process_held = None

        timestamp_min = time.time()
        process_min = self

        for process in processes:
            if process.state == State.HELD:
                process_held = process
            elif process.state == State.WANTED:
                if process.request_timestamp < timestamp_min:
                    timestamp_min = process.request_timestamp
                    process_min = process

        if process_held is None:
            cs = CriticalSection()
            cs.give_access(process_min)



def generate_processes(N):
    global processes
    processes = [Process(id + 1, State.DO_NOT_WANT, 5, 10) for id in range(N)]


def start_processes():
    for process in processes:
        process.start()


def execute_command(input_command):
    cmd = input_command.lower().split()
    command = cmd[0]

    if command == 'list':
        try:
            list()
        except:
            print("Error")

    if command == 'time-p':
        try:
            update_upper_delay(int(cmd[1]))
        except:
            print("Error")

    if command == 'time-cs':
        try:
            update_upper_cs(int(cmd[1]))
        except:
            print("Error")

    if command == 'exit':
        return False

    return True


def list():
    for p in processes:
        print(f"P{p.id}, {p.state.value}, Upper_time: {p.request_delay_time_upper}", end="\n")

def update_upper_delay(t):
    for p in processes:
        p.request_delay_time_upper = t


def update_upper_cs(t):
    for p in processes:
        p.critical_section_time_upper = t

if __name__ == "__main__":
    node = Node(1, 8001)
    node.start()

    # N = 6
    # generate_processes(N)
    # start_processes()
    # running = True
    # while running:
    #     command = input("Command: ")
    #     running = execute_command(command)
