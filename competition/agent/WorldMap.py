from copy import deepcopy, copy


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

        for move, new_state_after_move in self.get_all_possible_moves():
            print(move)
            print(new_state_after_move)
            
            possible_moves_dict[move] = new_state_after_move

        return possible_moves_dict

    def get_all_possible_moves(self):

        for card in self.state["player_hand"]: # Moves for cards in hand
            if card['type'] == 'minion':
                new_state_after_move = self.compute_new_state_for_card(card, self.state)
                is_move_possible = self.is_move_possible(card, self.state, new_state_after_move)

                if is_move_possible:
                    move = (1, (card['zone_position'], None))
                    yield move, new_state_after_move

            if card['type'] == 'spell':
                for target in self.state['opponent_target']:
                    new_state_after_move = self.compute_new_state_for_card(card, self.state, target)
                    is_move_possible = self.is_move_possible(card, self.state, new_state_after_move)

                    if is_move_possible:
                        move = (2, (card['zone_position'], target['zone_position']))
                        yield move, new_state_after_move

        for card in self.state['player_target']: # Moves for minions on the board
            if card['type'] == 'minion':
                for target in self.state['opponent_target']:
                    new_state_after_move = self.compute_new_state_for_card(card, self.state, target)
                    is_move_possible = self.is_move_possible(card, self.state, new_state_after_move)

                    if is_move_possible:
                        move = (3, (card['zone_position'], target['zone_position']))
                        yield move, new_state_after_move


        if self.state["player_mana"] >= 2: # Hero power
            new_state_after_move = deepcopy(self.state)
            new_state_after_move['player_mana'] -= 2
            new_state_after_move['opponent_target'][0]['health'] -= 2 # Target enemy hero

            yield (0, (None, None)), new_state_after_move

    def compute_new_state_for_card(self, card, state, target=None):
        # TODO: check minion/spell special effects

        new_state_after_move = deepcopy(state)
        if card["type"] == "minion":
            if target is None: # If played from hand
                new_state_after_move['player_target'].append(card) # Add card to the board state
                new_state_after_move['player_hand'].pop(card['zone_position']-1) # Remove card from hand

            elif target != None and card['cant_attack'] is False: # Attacking with the minion from board and you can use it.
                if target['type'] == 'hero':
                    new_state_after_move['opponent_target'][0]['health'] -= card['atk'] # Remove

                elif target['type'] == 'minion':
                    if target['atk'] >= card['health'] and card['atk'] >= target['health']: # If both minions die
                        new_state_after_move['player_target'].pop(card['zone_position']-1) # Kill our minion
                        new_state_after_move['opponent_target'].pop(target['zone_position']-1) # Kill their minion

                    elif target['atk'] >= card['health']: # If our minion dies
                        new_state_after_move['player_target'].pop(card['zone_position']-1) # Kill our minion
                        new_state_after_move['opponent_target'][target['zone_position']-1]['health'] -= card['atk'] # Update their minion's hp

                    elif card['atk'] >= target['health']: # If their minion dies
                        new_state_after_move['opponent_target'].pop(target['zone_position']-1) # Kill their minion
                        new_state_after_move['player_target'][card['zone_position']-1]['health'] -= target['atk'] # Update our minion's hp

        elif card["type"] == "spell":
            pass


        return new_state_after_move  # TODO: effectively change the state.

    def is_move_possible(self, card, state, new_state_after_move):
        mana = copy(new_state_after_move['player_mana'])

        if mana >= 0:
            return True

        return False
