import socket
import threading

import rpyc
from rpyc.utils.server import ThreadedServer
import datetime
import _thread
import time
import random

from StateEnum import State
from CriticalSectionClass import CriticalSection
from ProcessClass import Process
from node import Node

processes = []


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
