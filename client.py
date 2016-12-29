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

def display_grid(player_num, grid):
	message = "-------------" + "\n"
	for i in range(3):
		message += "| " + symbols[grid.cells[i*3]]
		message += " | " + symbols[grid.cells[i*3+1]]
		message += " | " + symbols[grid.cells[i*3+2]] + " |" + "\n"
		message += "-------------" + "\n"
	players[player_num-1].send(message.encode())

def getsock(player_num):
	return players[player_num-1]
