from agent.data_builder import *


def test_data_saver():
    d = DataSaver()
    d.add_json((1, None, 2), 1)


def test_wm():
    wm = {'n_opponent_hand': 4,
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

    start()
    play(wm)
    play(wm)
    play(wm)
    play(wm)
    end(True)


if __name__ == "__main__":
    pass
    # test_data_saver()
    test_wm()
