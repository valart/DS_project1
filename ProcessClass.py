import time
import random
import _thread
import enum

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