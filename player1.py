#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    author: Serhii Ivanov
    github: https://github.com/Siromanec/project3_game_tetris
    This bot sometimes makes mistakes, but easily
    fills entire board
    ...a pretty bad bot to be honest -_-
"""
from typing import List
from logging import DEBUG, debug, getLogger

getLogger().setLevel(DEBUG)


def parse_field_info():
    """
    Parse the info about the field.
    However, the function doesn't do anything with it.
    Since the height of the field is
    hard-coded later, this bot won't work with maps of different height.
    The input may look like this:
    Plateau 15 17:
    """
    l = input()
    try:
        size = int(l.split()[1]), int(l.split()[2].replace(":", ''))
    except IndexError:
        raise Exception("Enter field info according to the standart")
    return size


def parse_field(player: int, size: tuple):
    """
    :param int player: number of the player
    :param tuple size: size of the board
    The input may look like this:
        01234567890123456
    000 .................
    001 .................
    002 .................
    003 .................
    004 .................
    005 .................
    006 .................
    007 ..O..............
    008 ..OOO............
    009 .................
    010 .................
    011 .................
    012 ..............X..
    013 .................
    014 .................
    """
    coords_set_friend = set()
    coords_set_enemy = set()
    for i in range(size[0]+1):
        l = input()
        c = l.lower().find("o" if player == 1 else "x")
        if c != -1:
            try:
                coords = 0
                height = int(l[:3])
                for j in l.lower():
                    if j == ("o" if player == 1 else "x"):
                        coords_set_friend.add((height, coords-4))
                    coords += 1
            except ValueError:
                pass
        c = l.lower().find("x" if player == 1 else "o")
        if c != -1:
            try:
                coords = 0
                height = int(l[:3])
                for j in l.lower():
                    if j == ("x" if player == 1 else "o"):
                        coords_set_enemy.add((height, coords-4))
                    coords += 1
            except ValueError:
                pass
    return coords_set_friend, coords_set_enemy


def parse_figure():
    """
    Returns info about the figurue, such as: vertices,
                                             size,
                                             boundaries
    The input may look like this:
    Piece 2 2:
    **
    ..
    """
    l = input()
    piece_set = set()
    piece_size = int(l.split()[1]), int(l.split()[2].replace(":", ''))
    for _ in range(piece_size[0]):
        l = input()
        coords = 0
        for j in l.lower():
            if j == "*":
                piece_set.add((_, coords))
            coords += 1
    vertical, horizontal = circumcise(piece_set)

    return piece_set, piece_size, vertical, horizontal


def circumcise(piece_set: set) -> tuple:
    """
    cuts off all unnecesary dots to speed up calculations
    :param set piece_set: vertices of the figure

    :return tuple(tuple): tuple of all boundaries

    """
    right = max(piece_set, key=lambda x: x[1])[1]
    left = min(piece_set, key=lambda x: x[1])[1]
    upper = max(piece_set, key=lambda x: x[0])[0]
    lower = min(piece_set, key=lambda x: x[0])[0]

    return (right, left), (upper, lower)


def step(player: int,
         turn: int,
         last_move: tuple,
         token: bool,
         set_orientation: bool):
    """
    Perform one step of the game.
    :param player int: Represents whether we're the first or second player
    :param int turn: value for the turn iteration
    :param tuple last_move: the coordinates of the last move
    :param bool token: for making sure which way to go
    :param bool set_orientation: checks orientation of the start (up or down)
    :return tuple move: the actual move the bot wants to make
    :return bool token: returns token so the program doesn't calculate it more
                        than once
    :return bool orientation: returns orientation so the program doesn't
                              calculate it more than once

    """
    plateau_size = parse_field_info()
    coords_set_friend, coords_set_enemy = parse_field(player, plateau_size)
    piece_set, piece_size, vertical, horizontal = parse_figure()
    possible_moves = set()
    for i in coords_set_friend:
        posible_coords = generate_possible_coords(i,
                                                  piece_size,
                                                  plateau_size,
                                                  vertical,
                                                  horizontal)
        for coord in posible_coords:
            if check_possibility(coord,
                                 piece_set,
                                 coords_set_friend,
                                 coords_set_enemy,
                                 plateau_size):
                possible_moves.add(coord)
    if turn == 1:
        starting_location_friend = next(iter(coords_set_friend))
        orientation = plateau_size[0]//2 > starting_location_friend[0]
    else:
        orientation = set_orientation
    return make_move(last_move, possible_moves, plateau_size, token, orientation)


def make_move(last_move: tuple, possible_moves: set, plateau_size: tuple, token: bool, orientation: bool)->tuple:
    """
    the bot's logic
    :param tuple last_move:
    :param set possible_moves:
    :param tuple plateu_size:
    :param bool token:
    :param bool orientation:

    :return tuple
    
    """
    try:
        if not orientation:
            if not token:
                if last_move[0] - 4 < 0 or last_move[1] - 4 < 0:
                    move = max(possible_moves, key=lambda x: x[0] + x[1])
                elif (last_move[0] + 4 < plateau_size[0] or
                      last_move[1] + 4 < plateau_size[1]):
                    token = False
                    move = min(possible_moves, key=lambda x: x[0] + x[1])
                else:
                    token = True
                    move = min(possible_moves, key=lambda x: x[0] + x[1])
            else:
                move = min(possible_moves, key=lambda x: x[0] + x[1])
        else:
            if not token:
                if last_move[0] < 0 or last_move[1] < 0:
                    move = min(possible_moves, key=lambda x: x[0] + x[1])
                elif (last_move[0] < plateau_size[0] or
                      last_move[1] < plateau_size[1]):
                    token = False
                    move = max(possible_moves, key=lambda x: x[0] + x[1])
                else:
                    token = True
                    move = max(possible_moves, key=lambda x: x[0] + x[1])
            else:
                move = max(possible_moves, key=lambda x: x[0] + x[1])
        return move, token, orientation
    except ValueError:
        return ("Cannot put the figure")


def check_possibility(posible_coords: tuple,
                      figure_coords: List[tuple],
                      coords_set_friend: List[tuple],
                      coords_set_enemy: List[tuple],
                      plateau_size: tuple) -> bool:
    """
    Checks if it is possible to nput a figure at certain coordinates
    :param tuple posible_coords: all possible coords
    :param List[tuple] figure_coords: vertices of the  figure
    :param List[tuple] coords_dict_friend: all friendly coords
    :param List[tuple] coords_dict_enemy: all friendly coords
    :param tuple plateau_size: size of the plateau

    :return bool: if True, then bot van place a figure there

    """
    possible_real_coords = set()
    for coord in figure_coords:
        real_height = posible_coords[0] + coord[0]
        real_length = posible_coords[1] + coord[1]
        possible_real_coords.add((real_height, real_length))
    
    count = 0
    enemy_count = 0

    for coords in possible_real_coords:

        if coords[0] == plateau_size[0] or coords[1] == plateau_size[1]:
            return False

        if coords in coords_set_friend:
            count += 1
            if count > 1:
                return False

        if coords in coords_set_enemy:
            enemy_count += 1
            if enemy_count > 0:
                return False

    return count == 1 and enemy_count == 0


def generate_possible_coords(point_coords: tuple,
                             piece_size: tuple,
                             plateau_size: tuple,
                             vertical: tuple,
                             horizontal: tuple) -> set:
    """
    generates all possible moves at a certain point
    :param tuple point_coords: point that is checked 
    :param tuple piece_size: size of the piece
    :param tuple plateau_size: size of the plateau
    :param tuple vertical: boundaries that are set vertically
    :param tuple horizontal: boundaries that are set horizontally
    :return set posible_coords: set of all possible coords
    """
    plateau_height, plateau_length = plateau_size
    posible_coords = set()
    main_height = point_coords[0]
    main_length = point_coords[1]

    for height in range(abs(horizontal[1]-horizontal[0])+1):

        for length in range(abs(vertical[1]-vertical[0])+1):

            minus_height = main_height - height - horizontal[0]
            plus_height = main_height + height - horizontal[0]
            minus_length = main_length - length - vertical[0]
            plus_length = main_length + length - vertical[0]

            if (plateau_height - piece_size[0] + 1 > plus_height > 0 and
               plateau_length - piece_size[1] + 1 > plus_length > 0):
                posible_coords.add((plus_height, plus_length))

            if (plateau_length - piece_size[1] + 1 > plus_length > 0 and
               minus_height + 1 > 0):
                posible_coords.add((minus_height, plus_length))

            if (plateau_height - piece_size[0] + 1 > plus_height > 0 and
               minus_length + 1 > 0):
                posible_coords.add((plus_height, minus_length))

            if (minus_height + 1 > 0 and
               minus_length + 1 > 0):
                posible_coords.add((minus_height, minus_length))
    return posible_coords


def play(player: int):
    """
    Main game loop.
    :param player int: Represents whether we're the first or second player
    """
    turn = 0
    token = False
    move = (10000000, 1000000)
    set_orientation = False
    while True:
        turn += 1
        try:
            move, token, set_orientation = step(player,
                                                turn,
                                                move,
                                                token,
                                                set_orientation)
            print(*move)
        except ValueError:
            print("Cannot put the figure")


def parse_info_about_player():
    """
    This function parses the info about the player
    It can look like this:
    $$$ exec p2 : [./player1.py]
    """
    i = input()
    debug(f"Info about the player: {i}")
    return 1 if "p1 :" in i else 2


def main():
    player = parse_info_about_player()
    try:
        play(player)
    except EOFError:
        pass


if __name__ == "__main__":
    main()
