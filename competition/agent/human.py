import sys
import pprint


# Modify this function
def start():
    return None


def play(state, stdin):
    # Modify this function
        print('=========================================')
        print('Start turn')
        print('=========================================')
        pprint.pprint(state)
        sys.stdin = stdin
        action = int(input('Action: ')[0])
        if action == 0 or action == 4:
            return action, None
        argument1 = int(input('Argument 1: '))
        if action == 1:
            return action, argument1
        argument2 = int(input('Argument 2: '))
        return action, (argument1, argument2)


# Modify this function
def end(victory):
    return None


# Don't touch this function
def communicate(pipe, stdin, *args, **kwargs):
    while True:
        packet = pipe.recv()
        action = packet['action']
        sys.stdin = stdin
        if action == 'start':
            pipe.send(start())
        elif action == 'play':
            out = play(packet['args'], stdin)
            pipe.send(out)
        elif action == 'end':
            pipe.send(end([packet['args']]))


class CommunicateDebug:
    def __init__(self, stdin, *args):
        self.stdin = stdin
        self.out = None

    def send(self, packet):
        action = packet['action']
        if action == 'start':
            start()
        elif action == 'play':
            self.out = play(packet['args'], self.stdin)
        elif action == 'end':
            end([packet['args']])

    def recv(self):
        return self.out
