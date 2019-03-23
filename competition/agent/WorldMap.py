from copy import deepcopy


class WorldMap:
    def __init__(self, state):
        """

        :param state:

        {'n_opponent_hand': 4,
         'opponent_health': 30,
         'opponent_mana': 1,
         'opponent_target': [{'damaged': False,
                              'dead': False,
                              'health': 30,
                              'id': 'HERO_05',
                              'type': 'hero',
                              'zone_position': 0}],
         'player_hand': [{'atk': 1,
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
                          'zone_position': 1},
                         {'cost': 3, 'id': 12, 'type': 'spell', 'zone_position': 2},
                         {'atk': 3,
                          'buffs': [],
                          'cant_attack': False,
                          'cost': 2,
                          'damaged': False,
                          'health': 2,
                          'id': 8,
                          'max_health': 2,
                          'poisonous': False,
                          'powered_up': False,
                          'turns_in_play': 0,
                          'type': 'minion',
                          'zone_position': 3},
                         {'cost': 1, 'id': 3, 'type': 'spell', 'zone_position': 4},
                         {'atk': 1,
                          'buffs': [],
                          'cant_attack': False,
                          'cost': 1,
                          'damaged': False,
                          'health': 1,
                          'id': 4,
                          'max_health': 1,
                          'poisonous': False,
                          'powered_up': False,
                          'turns_in_play': 0,
                          'type': 'minion',
                          'zone_position': 5}],
         'player_health': 30,
         'player_mana': 1,
         'player_target': [{'damaged': False,
                            'dead': False,
                            'health': 30,
                            'id': 'HERO_05',
                            'type': 'hero',
                            'zone_position': 0}]}
        """
        self.state = state

    def get_possible_moves(self):
        possible_moves_dict = dict()

        for is_move_possible, move, new_state_after_move in self.get_all_possible_moves():
            possible_moves_dict[move] = new_state_after_move

        return possible_moves_dict

    def get_all_possible_moves(self):

        for card in self.state["player_hand"]:
            new_state_after_move = self.compute_new_state_for_card(card, self.state)

            is_move_possible = self.is_move_possible(card, self.state, new_state_after_move)

            if is_move_possible:
                move = 4, (None, None)
                yield is_move_possible, move, new_state_after_move

        if self.state["player_mana"] >= 2:
            yield True,

    def compute_new_state_for_card(self, card, state):
        if card["type"] == "minion":
            pass
        elif card["type"] == "":
            pass
        return deepcopy(state)  # TODO: effectively change the state.

    def is_move_possible(self, cards, state, new_state_after_move):
        return False  # TODO: check mana.
