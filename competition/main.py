#!/usr/bin/env python
import os
import sys
import argparse
from multiprocessing import Process, Pipe
import importlib

from fireplace import cards
from fireplace.exceptions import GameOver
from fireplace import utils


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agent1', type=str, required=True, help='First agent module')
    parser.add_argument('--agent2', type=str, required=True, help='Second agent module')
    parser.add_argument('--n-games', type=int, default=1, help='Number of games to run')
    parser.add_argument('--debug', action='store_true',
                        help='Debug version. Will disable spawning process for each agent')
    return parser.parse_args()


def use_hp(player, *args):
    heropower = player.hero.power
    if not heropower.is_usable():
        return True
    heropower.use()
    return False


def play_card(player, dest, card_position, target, *args):
    cards = player.hand
    if card_position > len(cards):
        return True
    card = cards[card_position]
    if not card.is_playable():
        return True
    targets = [dest.hero] + [dest.field]
    t = targets[target]
    if 'List' in str(type(t)) or type(t) == 'list':
        t = t[0]
    card.play(target=t)
    return False


def attack(player, adversary, source, target, *args):
    character = [player.hero] + player.field
    character = character[source]
    if 'List' in str(type(character)) or type(character) == 'list':
        character = character[0]
    if not character.can_attack():
        return True
    character.attack(character.targets[target])
    return False


def serialize_minion(x):
    attributes = [
            'atk',
            'buffs',
            'cant_attack',
            'cost',
            'damaged',
            'health',
            'id',
            'max_health',
            'powered_up',
            'poisonous',
            'turns_in_play',
            'zone_position'
            ]
    minion = {attribute: getattr(x, attribute) for attribute in attributes}
    minion['type'] = 'minion'
    return minion


def serialize_hero(x):
    attributes = [
            'damaged',
            'dead',
            'health',
            'id',
            'zone_position'
            ]
    hero = {attribute: getattr(x, attribute) for attribute in attributes}
    hero['type'] = 'hero'
    return hero


def serialize_spell(x):
    attributes = [
            'cost',
            'id',
            'zone_position'
            ]
    spell = {attribute: getattr(x, attribute) for attribute in attributes}
    spell['type'] = 'spell'
    return spell


def serialize(x):
    t = str(type(x)).split('.')[-1].replace('>', '').replace("'", "")
    if t == 'Minion':
            return serialize_minion(x)
    if t == 'Hero':
            return serialize_hero(x)
    if t == 'Spell':
            return serialize_spell(x)


def construct_state(player, adversary):
    state = dict()
    state['player_hand'] = [serialize(x) for x in player.hand]
    state['player_target'] = [serialize(player.hero)] + [serialize(x) for x in player.field]
    state['opponent_target'] = [serialize(adversary.hero)] + [serialize(x) for x in adversary.field]
    state['player_health'] = player.hero.health
    state['opponent_health'] = player.opponent.hero.health
    state['player_mana'] = int(str(player.mana))
    state['opponent_mana'] = int(str(adversary.mana))
    state['n_opponent_hand'] = len(player.opponent.hand)
    return state


def play_game(comm1, comm2):
    print('Game on')
    game = utils.setup_game()
    for player in game.players:
            player.choice.choose()
    while True:
        try:
            for comm in (comm1, comm2):
                player = game.current_player
                adversary = game.player1 if game.player1 != player else game.player2
                end = False
                while not end:
                    state = construct_state(player, adversary)
                    packet = {'action': 'play', 'args': state}
                    try:
                        comm.send(packet)
                        answer = comm.recv()
                        action = answer[0]
                        if action == 0:
                                end = use_hp(player)
                        elif action == 1:
                                card = answer[1] if type(answer[1]) is int else answer[1][0]
                                end = play_card(player, player, card, 0)
                        elif action == 2:
                                end = play_card(player, adversary, *answer[1])
                        elif action == 3:
                                end = attack(player, adversary, *answer[1])
                        else:
                                end = True
                    except Exception as e:
                        print(e)
                        end = True
                game.end_turn()
        except GameOver:
            if not game.player1.hero.dead:
                packet = {'action': 'end', 'args': True}
                comm1.send(packet)
            else:
                packet = {'action': 'end', 'args': False}
                comm1.send(packet)
            if not game.player2.hero.dead:
                packet = {'action': 'end', 'args': True}
                comm2.send(packet)
            else:
                packet = {'action': 'end', 'args': False}
                comm2.send(packet)
            comm1.recv()
            comm2.recv()
            return


def launch_debug(agent1, agent2, stdin, n_games):
    comm1 = agent1.CommunicateDebug(stdin)
    comm2 = agent2.CommunicateDebug(stdin)
    for _ in range(n_games):
        packet = {'action': 'start', 'args': None}
        comm1.send(packet)
        comm2.send(packet)
        comm1.recv()
        comm2.recv()
        play_game(comm1, comm2)


def launch_game(agent1, agent2, stdin, n_games):
    for _ in range(n_games):
        comm1, comm_child1 = Pipe()
        child1 = Process(target=agent1.communicate, args=(comm_child1, stdin))
        comm2, comm_child2 = Pipe()
        child2 = Process(target=agent2.communicate, args=(comm_child2, stdin))
        child1.start()
        child2.start()
        packet = {'action': 'start', 'args': None}
        comm1.send(packet)
        comm2.send(packet)
        comm1.recv()
        comm2.recv()
        play_game(comm1, comm2)
        comm1.close()
        comm2.close()
        child1.terminate()
        child2.terminate()


def main(args):
    cards.db.initialize()
    agent1 = importlib.import_module(args.agent1)
    agent2 = importlib.import_module(args.agent2)
    stdin = os.fdopen(os.dup(sys.stdin.fileno()))
    if args.debug:
        launch_debug(agent1, agent2, stdin, args.n_games)
    else:
        launch_game(agent1, agent2, stdin, args.n_games)


if __name__ == "__main__":
    args = parse_args()
    main(args)
