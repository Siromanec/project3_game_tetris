#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    This is an example of a bot for the 3rd project.
    ...a pretty bad bot to be honest -_-
"""
from typing import List
from logging import DEBUG, debug, getLogger
import random
# We use the debugger to print messages to stderr
# You cannot use print as you usually do, the vm would intercept it
# You can hovever do the following:
#
# import sys
# print("HEHEY", file=sys.stderr)

getLogger().setLevel(DEBUG)


def parse_field_info():
    """
    Parse the info about the field.
    However, the function doesn't do anything with it. Since the height of the field is
    hard-coded later, this bot won't work with maps of different height.
    The input may look like this:
    Plateau 15 17:
    """
    l = input()
    #debug(f"Description of the field: {l}")
    try:
        size = int(l.split()[1]), int(l.split()[2].replace(":",''))
    except IndexError:
        raise Exception("Enter field info according to the standart")
    return size


def parse_field(player: int, size: tuple):
    """
    Parse the field.
    First of all, this function is also responsible for determining the next
    move. Actually, this function should rather only parse the field, and return
    it to another function, where the logic for choosing the move will be.
    Also, the algorithm for choosing the right move is wrong. This function
    finds the first position of _our_ character, and outputs it. However, it
    doesn't guarantee that the figure will be connected to only one cell of our
    territory. It can not be connected at all (for example, when the figure has
    empty cells), or it can be connected with multiple cells of our territory.
    That's definitely what you should address.
    Also, it might be useful to distinguish between lowecase (the most recent piece)
    and uppercase letters to determine where the enemy is moving etc.
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
    :param player int: Represents whether we're the first or second player
    """
    move = None
    coords_set_friend = set()
    coords_set_enemy = set()
    for i in range(size[0]+1):
        l = input()
        #debug(f"Field: {l}")
        if move is None:
            c = l.lower().find("o" if player == 1 else "x")
            if c != -1:
                try:
                    lengths = read_map(player, l)
                    for j in lengths:
                        coords_set_friend.add((int(l[:3]),j))
                except ValueError:
                    pass
        if move is None:
            c = l.lower().find("x" if player == 1 else "o")
            if c != -1:
                try:
                    lengths = read_map(1 if player == 2 else 2, l)
                    for j in lengths:
                        coords_set_enemy.add((int(l[:3]),j))
                except ValueError:
                    pass
    #debug( coords_dict_friend)
    #debug( coords_dict_enemy)

    return coords_set_friend, coords_set_enemy

def read_map(player:int, line:str)->list:
    """
    finds enemies and friends
    :param int player:
    :param str line:

    :return list
    
    """
    line_taken = set()
    coords = 0
    for j in line.lower():
        if j == ("o" if player == 1 else "x"):
            line_taken.add(coords-4)
        coords+=1
    return line_taken


def parse_figure():
    """
    Parse the figure.
    The function parses the height of the figure (maybe the width would be
    useful as well), and then reads it.
    It would be nice to save it and return for further usage.
    The input may look like this:
    Piece 2 2:
    **
    ..
    """
    l = input()
    #debug(f"Piece: {l}")
    piece_set = set()
    piece_size = int(l.split()[1]), int(l.split()[2].replace(":",''))
    for _ in range(piece_size[0]):
        l = input()
        #debug(f"Piece: {l}")
        coords = 0
        for j in l.lower():
            if j == "*":
                piece_set.add((_,coords))
            coords+=1
    vertical, horizontal = circumcise(piece_set)

    return piece_set, piece_size, vertical, horizontal

def circumcise(piece_set:set)->tuple:
    """
    cuts off all unnecesary dots to speed up calculations
    :param set piece_set:

    :return tuple
    
    """
    right = max(piece_set, key=lambda x:x[1])[1]
    left = min(piece_set, key=lambda x:x[1])[1]
    upper = max(piece_set, key=lambda x:x[0])[0]
    lower = min(piece_set, key=lambda x:x[0])[0]



    return (right, left), (upper, lower)
        
    


def step(player: int, turn):
    """
    Perform one step of the game.
    :param player int: Represents whether we're the first or second player
    """
    plateau_size = parse_field_info()
    coords_set_friend, coords_set_enemy = parse_field(player, plateau_size)
    piece_set, piece_size, vertical, horizontal = parse_figure()
    possible_moves = set()
    for i in coords_set_friend:
        posible_coords = generate_possible_coords(i, piece_size, plateau_size, coords_set_friend, vertical, horizontal, piece_set)
        for j in posible_coords:
            #debug(piece_set)
            if check_possibility(j, piece_set, coords_set_friend, coords_set_enemy, plateau_size):
                #debug("True")
                possible_moves.add(j)
    #debug(possible_moves])
    for i in possible_moves:

        if turn < (plateau_size[0]**2 +plateau_size[1]**2)**(1/2)/4:
            return min(possible_moves, key = lambda x: x[0] + x[1])
        return max(possible_moves, key = lambda x: x[0] + x[1])

    #for i in coords_set_friend:
    #    if i[0] in range(plateau_size[0]//2):
    #        if i[1] in range(plateau_size[1]//2):
    #            return max(possible_moves, key = lambda x: x[1])
    #        else:
    #            return min(possible_moves, key = lambda x: x[1])
    #    else:
    #        if i[1] in range(plateau_size[1]//2):
#
    #           return min(possible_moves, key = lambda x: x[0])
#
    #        else:
    #            return max(possible_moves, key = lambda x: x[0])


def check_possibility(posible_coords: tuple,
                      figure_coords: List[tuple], 
                      coords_set_friend: List[tuple], 
                      coords_set_enemy: List[tuple],
                      plateau_size: tuple)->bool:
    """
    Checks if it is possible to nput a figure at certain coordinates
    :param tuple posible_coords:
    :param dict(list) figure_coords:
    :param dict(list) coords_dict_friend:
    :param dict(list) coords_dict_enemy:

    :return bool
    
    """
    #screen if shape goes in
    possible_real_coords = set()
    for coord in figure_coords:
        real_height = posible_coords[0] + coord[0]
        real_length = posible_coords[1] + coord[1]
        possible_real_coords.add((real_height, real_length))
    count = 0
    enemy_count = 0
#debug(possible_real_coords)
    for coords in possible_real_coords:
        if coords[0] == plateau_size[0] or coords[1] == plateau_size[1]:
            return False
        if coords in coords_set_friend:
            count+=1
            if count>1:
                return False
        
        
        if coords in coords_set_enemy:
            #debug(True)
            enemy_count+=1
            if enemy_count > 0:
                return False
    return count == 1 and enemy_count == 0

def generate_possible_coords(point_coords:tuple, piece_size:tuple, plateau_size:tuple, coords_set_friend: List[tuple], vertical, horizontal, figure_coords)->dict:
    """
    generates all possible moves at a certain point
    :param tuple point_coords:
    :param tuple piece_size:

    :return dict
    
    """
   
    #grid_height =  [x for x in range(vertical[0]+1)]
    #grid_length =  [x for x in range(horizontal[0]+1)]
    #grid_height.reverse()
    #grid_length.reverse()
    ##debug(f"h: {grid_height}")
    ##debug(f"l: {grid_length}")
    ##debug(f"v: {vertical}")
    ##debug(f"h: {horizontal}")
    ##debug(f"c: {figure_coords}")
    #projection = set()
    ##fix looped index or find another way to rotate
    #for i in figure_coords:
    #    length, height = i
    #    #debug(f"{grid_height}, {[height]}")
    #    #debug(f"{grid_length}, {[length]}")
    #    half_rotation = grid_height[height], grid_length[length]
    #    relative_coords = point_coords[0] - half_rotation[0], point_coords[1] - half_rotation[1]
    #    if relative_coords[0] +vertical[1]-1 > 0 and relative_coords[1] + horizontal[1] -1 > 0:
    #        projection.add(relative_coords)
    #    
    #return projection
    #
    plateau_height, plateau_length = plateau_size
    posible_coords = set()
    main_height = point_coords[0]
    main_length = point_coords[1]
    ###if 0 in point_coords or plateau_height or plateau_length in point_coords:
    ###    return set()
    surrounding = ((main_height + 1, main_length + 1),
                   (main_height + 1, main_length - 1),
                   (main_height + 1, main_length + 0),
                   (main_height + 0, main_length + 1),
                   (main_height + 0, main_length - 1),
                   (main_height + 1, main_length + 0),
                   (main_height - 1, main_length - 1),
                   (main_height - 1, main_length + 1))
    count = 0
    for i in surrounding:
        if i in coords_set_friend:
            count += 1
    if count == 8:
        return set()
    #
    for height in range(abs(horizontal[1]-horizontal[0])+1):

        for length in range(abs(vertical[1]-vertical[0])+1):

            minus_height = main_height - height - horizontal[0]
            plus_height = main_height + height - horizontal[0]
            minus_length = main_length - length - vertical[0]
            plus_length = main_length + length - vertical[0]

            if plateau_height - piece_size[0] -1 > plus_height and plateau_length - piece_size[1] -1 > plus_length:
                posible_coords.add((plus_height, plus_length))

            if plateau_length - piece_size[1] -1> plus_length and minus_height -1> 0:
                posible_coords.add((minus_height, plus_length))

            if plateau_height - piece_size[0] -1 > plus_height and minus_length -2> 0:
                posible_coords.add((plus_height, minus_length))

            if minus_height - 1> 0 and minus_length -2 > 0:
                posible_coords.add((minus_height, minus_length))
    #debug(point_coords)
    #debug(posible_coords)
    return posible_coords

def play(player: int):
    """
    Main game loop.
    :param player int: Represents whether we're the first or second player
    """
    turn = 0
    while True:
        turn+=1
        move= step(player, turn)
        print(*move)


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
        debug("Cannot get input. Seems that we've lost ):")


if __name__ == "__main__":
    main()
