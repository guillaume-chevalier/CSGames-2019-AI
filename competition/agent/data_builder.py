import statistics

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

from agent.WorldMap import WorldMap

WORLD_MAP = None
PIPELINE = None


# Modify this function
class Featurize(BaseEstimator, TransformerMixin):

    def fit(self, X, y):
        return self

    def transform(self, X, y=None, **fit_params):
        """
        Convert world map state's dicts to np.array of ML features.

        :param X: A list of world map's states.
        :param y: None
        :param fit_params:
        :return:
        """

        X = [self.transform_one(x) for x in X]
        return np.array(X)

    def transform_one(self, x):
        state = x
        new_x = []
        MAX_NUM_CARDS = 16  # TODO: 25?.

        # STATIC:
        new_x.append(state['player_health'])
        new_x.append(state['player_mana'])
        new_x.append(state['n_opponent_hand'])
        new_x.append(state['opponent_health'])
        new_x.append(state['opponent_mana'])

        # HEROS:
        at_least_two_heros = 0
        for target_key in ["opponent_target", "player_target"]:
            for target in state[target_key]:
                """
                _target = {'damaged': False,
                          'dead': False,
                          'health': 30,
                          'id': 'HERO_05',
                          'type': 'hero',
                          'zone_position': 0} 
                """
                if target['type'] == "hero":
                    at_least_two_heros += 1
                    new_x.append(int(target["damaged"]))
                    new_x.append(target["health"])
                    # new_x.append(target["zone_position"])
        assert at_least_two_heros == 2, "FAILURE."  # TODO: remove all asserts.

        # MY PLAYER CARDS:
        my_cards = [0 for _ in range(MAX_NUM_CARDS)]
        my_cards_costs = [0 for _ in range(MAX_NUM_CARDS)]  # TODO: number of cards.
        for card in state["player_hand"]:
            #  _card = {'cost': 3, 'id': 12, 'type': 'spell', 'zone_position': 2}
            if card["type"] == "spell":
                my_cards[card['id']] += 1
                my_cards_costs[card['id']] = card["cost"]
                # TODO: get attack of each card.
        new_x += my_cards
        new_x.append(sum(my_cards))
        new_x.append(sum(my_cards_costs))
        new_x.append(max(my_cards_costs))
        new_x.append(min(my_cards_costs))
        new_x.append(statistics.stdev(my_cards_costs))

        # PLAYER MINIONS:
        my_minions = [0 for _ in range(MAX_NUM_CARDS)]
        my_minions_hp = [0 for _ in range(MAX_NUM_CARDS)]
        my_minions_max_hp = [0 for _ in range(MAX_NUM_CARDS)]
        my_minions_buffs = [0 for _ in range(MAX_NUM_CARDS)]
        my_minions_cant_attack = [0 for _ in range(MAX_NUM_CARDS)]
        my_minions_atk = [0 for _ in range(MAX_NUM_CARDS)]
        my_minions_cost = [0 for _ in range(MAX_NUM_CARDS)]
        my_minions_damaged = [0 for _ in range(MAX_NUM_CARDS)]
        my_minions_poisonous = [0 for _ in range(MAX_NUM_CARDS)]
        my_minions_opwered = [0 for _ in range(MAX_NUM_CARDS)]
        my_minions_turns = [0 for _ in range(MAX_NUM_CARDS)]
        my_minions_zone_pos = [0 for _ in range(MAX_NUM_CARDS)]
        for minion in state["player_hand"]:
            """
            _minion = {'atk': 1,
                      'buffs': [],
                      'cant_attack': False,
                      'cost': 1,
                      'damaged': False,
                      'health': 1,
                      'id': 7,
                      'max_health': 1,
                      'poisonous': False,
                      'powered_up': False,
                      'turns_in_play': 0,
                      'type': 'minion',
                      'zone_position': 1}
            """
            if minion["type"] == "minion":
                _id = minion["id"]
                my_minions[_id] += 1
                my_minions_hp[_id] = minion["health"]
                my_minions_max_hp[_id] = minion["max_health"]
                my_minions_buffs[_id] = len(minion["buffs"])
                my_minions_cant_attack[_id] = int(minion["cant_attack"])
                my_minions_atk[_id] = minion["atk"]
                my_minions_cost[_id] = minion["cost"]
                my_minions_damaged[_id] = int(minion["damaged"])
                my_minions_poisonous[_id] = int(minion["poisonous"])
                my_minions_opwered[_id] = int(minion["powered_up"])
                my_minions_turns[_id] = minion["turns_in_play"]
                my_minions_zone_pos[_id] = minion["zone_position"]
                # TODO: maybe many minions with same ID.
        _features = [my_minions_hp,
                     my_minions_max_hp,
                     my_minions_buffs,
                     my_minions_cant_attack,
                     my_minions_atk,
                     my_minions_cost,
                     my_minions_damaged,
                     my_minions_poisonous,
                     my_minions_opwered,
                     my_minions_turns,
                     my_minions_zone_pos
                     ]
        for f in _features:
            new_x += f
            new_x.append(sum(f))
            new_x.append(max(f))
            new_x.append(min(f))
            new_x.append(statistics.stdev(f))


        # TARGETS:
        # TODO: finally this is same as PLAYER MINIONS above but on game.

        return None


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
