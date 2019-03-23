from pprint import pprint

from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

from agent.WorldMap import WorldMap

WORLD_MAP = None
PIPELINE = None


# Modify this function
class Featurize(BaseEstimator, TransformerMixin):

    def fit(self, X, y):
        return self

    def transform(self, X, y=None, **fit_params):
        pass


class NeuralNetwork(BaseEstimator, TransformerMixin):
    pass


def start():
    print('start')

    global PIPELINE
    if PIPELINE is not None:
        PIPELINE = Pipeline([
            ('featurize', Featurize()),
            ('model', NeuralNetwork())
        ])

    return None


# Modify this function
def play(state):
    global WORLD_MAP, PIPELINE
    if WORLD_MAP is None:
        WORLD_MAP = WorldMap(state)

    top_move = None
    top_move_score = -1
    """
    for move, new_state in WORLD_MAP.get_possible_moves().items():
        move_score = PIPELINE.transform(state, move, new_state)
        if move_score > top_move_score:
            top_move = move
    """
    print(WORLD_MAP.get_possible_moves())

    return 4, (None, None)


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
