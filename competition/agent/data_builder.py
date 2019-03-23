# Modify this function
def start():
    print('start')
    return None


# Modify this function
def play(state):
    return 'a', (None,)


# Modify this function
def end(victory):
    print(f'Victor: {victory}')
    return None


# Don't touch this function
def communicate(pipe, *args, **kwargs):
    while True:
        packet = pipe.recv()
        action = packet['action']
        if action == 'start':
            pipe.send(start())
        elif action == 'play':
            pipe.send(play(packet['args']))
        elif action == 'end':
            pipe.send(end([packet['args']]))


class CommunicateDebug:
    def __init__(self, *args):
        self.out = None

    def send(self, packet):
        action = packet['action']
        if action == 'start':
            start()
        elif action == 'play':
            self.out = play(packet['args'])
        elif action == 'end':
            end([packet['args']])

    def recv(self):
        return self.out

