import datetime
import json
import os
import pickle
import random
import statistics
from glob import glob

import numpy as np
import sklearn.neural_network
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.exceptions import NotFittedError
from sklearn.pipeline import Pipeline
from sklearn.utils.validation import check_is_fitted

from agent.WorldMap import WorldMap

PKL_MODEL_NAME = "model.pkl1"


class DataSaver:

    def __init__(self):
        self.json_path = "./training_jsons/"
        if not os.path.exists(self.json_path):
            os.mkdir(self.json_path)

        self.loaded_jsons = []
        self.loaded_jsons_y = []
        self.load_jsons()

    def load_jsons(self):
        self.loaded_jsons = []
        self.loaded_jsons_y = []

        jsons = glob(self.json_path + "*")

        for j in jsons[-1000:]:
            if ".json" in j:
                with open(j, "r", encoding="utf-8") as fppw:
                    jj = json.load(fppw)
                self.loaded_jsons.append(jj)
                filenamme = j.split(os.sep)[-1]
                this_y = int(filenamme[:1])
                self.loaded_jsons_y.append(this_y)

    def add_json(self, _json, was_success_integer):
        self._add_json(_json, was_success_integer)
        self.load_jsons()

    def add_jsons(self, _jsons, was_success_integers):
        for _json, was_success_integer in zip(_jsons, was_success_integers):
            self._add_json(_json, was_success_integer)
        self.load_jsons()

    def _add_json(self, _json, was_success_integer):
        _date = str(datetime.datetime.now()).replace(" ", "_").replace(":", "-")
        filename = os.path.join(self.json_path, str(was_success_integer) + "_" + _date + ".json")
        with open(filename, "w", encoding="utf-8") as fpp:
            # print(_json)
            json.dump(_json, fpp)

    def get_x_y(self):
        return self.loaded_jsons, self.loaded_jsons_y


random.seed(7)

PIPELINE = None
IS_TRAINING_WITH_RANDOM = True  # TODO: set to false to finalize.
IS_ONLINE_TRAINING = True  # TODO: set to false to finalize.
ALL_MY_MOVES_TRIPLETS = []
DS = DataSaver()


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
        state, move, new_state = x
        new_x = []
        MAX_NUM_CARDS = 16  # TODO: 25?.

        # Add the current state and expected state:
        self.process_a_state(MAX_NUM_CARDS, new_x, state)
        self.process_a_state(MAX_NUM_CARDS, new_x, new_state)

        # Add the move:
        new_x.append(move[0])
        a = move[1][0]
        b = move[1][1]
        new_x.append(a if a is not None else -1)
        new_x.append(b if b is not None else -1)

        new_x = [float(xx) for xx in new_x]
        return new_x

    def process_a_state(self, MAX_NUM_CARDS, new_x, state):
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
        self.extract_minions(MAX_NUM_CARDS, new_x, state, 0)
        self.extract_minions(MAX_NUM_CARDS, new_x, state, 1)
        self.extract_minions(MAX_NUM_CARDS, new_x, state, 2)

    def extract_minions(self, MAX_NUM_CARDS, new_x, state, idx=0):
        """
        new_x is updated to add what's seen.
        """
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
        key = ["player_hand", "opponent_target", "player_target"][int(idx)]

        for minion in state[key]:
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


class NeuralNetwork(sklearn.neural_network.MLPClassifier):

    def transform(self, X, y=None):
        return self.predict(X)


def start():
    random.seed(7)
    global PIPELINE, IS_TRAINING_WITH_RANDOM, IS_ONLINE_TRAINING, ALL_MY_MOVES_TRIPLETS, DS
    PIPELINE = None
    IS_TRAINING_WITH_RANDOM = True  # TODO: set to false to finalize.
    IS_ONLINE_TRAINING = True  # TODO: set to false to finalize.
    ALL_MY_MOVES_TRIPLETS = []
    DS = DataSaver()

    print('start')

    # LOAD MODEL.
    if os.path.exists(PKL_MODEL_NAME):
        with open(PKL_MODEL_NAME, "rb") as pkl:
            PIPELINE = pickle.load(pkl)

    # OR CREATE MODEL.
    if PIPELINE is None:
        PIPELINE = Pipeline([
            ('featurize', Featurize()),
            ('model', NeuralNetwork(
                # TODO: redo this.
                shuffle=False,
                early_stopping=True,
                n_iter_no_change=30,
                batch_size=2,
                random_state=7
            ))
        ])

    X, y = DS.get_x_y()
    if len(y) > 0:
        PIPELINE.fit(X, y)

    return None


# Modify this function
def play(state):
    global PIPELINE, ALL_MY_MOVES_TRIPLETS, IS_TRAINING_WITH_RANDOM
    world_map = WorldMap(state)

    top_move = None
    top_move_new_state = None
    top_move_score = -1

    for move, new_state in world_map.get_possible_moves().items():

        state = WorldMap.sanitize_state(state)
        new_state = WorldMap.sanitize_state(new_state)

        X = [(state, move, new_state)]
        try:
            _ = check_is_fitted(PIPELINE.named_steps["model"], "coefs_")
            move_score = PIPELINE.transform(X)[0]
        except NotFittedError as e:
            print("WARNING: RANDOM MOVE.")
            move_score = random.random()
            # print("WARNING: FIRST FIT.")
            # PIPELINE.fit(X*4, [1]*4)

        if IS_TRAINING_WITH_RANDOM:
            move_score += random.random() * 0.9

            print("----------", move, move_score)

        if move_score > top_move_score:
            top_move = move
            top_move_new_state = new_state
            top_move_score = move_score

    ALL_MY_MOVES_TRIPLETS.append(
        (state, top_move, top_move_new_state)
    )

    print("My move:", top_move)
    return top_move


# Modify this function4, (None, None)
def end(victory):
    if hasattr(victory, "__len__"):
        assert len(victory) == 1, victory
        victory = victory[0]

    print(f'Victor: {victory}. Training Neural Net:')
    global PIPELINE, ALL_MY_MOVES_TRIPLETS, IS_ONLINE_TRAINING, DS

    # RETRAIN.
    if IS_ONLINE_TRAINING:
        y = [int(victory) for _ in range(len(ALL_MY_MOVES_TRIPLETS))]
        DS.add_jsons(ALL_MY_MOVES_TRIPLETS, y)

        PIPELINE.fit(ALL_MY_MOVES_TRIPLETS, y)

        # SAVE.
        with open(PKL_MODEL_NAME, "wb") as pkl:
            pickle.dump(PIPELINE, pkl)

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
