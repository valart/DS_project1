import enum


class State(enum.Enum):
    HELD = 'HELD'
    WANTED = 'WANTED'
    DO_NOT_WANT = 'DO-NOT-WANT'
