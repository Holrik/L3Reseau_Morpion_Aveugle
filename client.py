#!/usr/bin/python3

from grid import *
from client import *
import socket

players = []

def newplayer(sock):
	for i in range(len(players)):
		if players[i] == -1:
			players[i] = sock
			break
	players.append(sock)

def delplayer(sock):
	for i in range(len(players)):
		if players[i] == sock:
			players[i] = -1
			break

def display_grid(player_num):
	message = "-------------"
	for i in range(3):
		message += "|" + symbols[grids[player_num].cells[i*3]] + "\n"
		message += "|" + symbols[grids[player_num].cells[i*3+1]] + "\n"
		message += "|" + symbols[grids[player_num].cells[i*3+2]] + "|" + "\n"
		message += "-------------" + "\n"
	players[player_num].send(message)

def getsock(player_num):
	return players[player_num]