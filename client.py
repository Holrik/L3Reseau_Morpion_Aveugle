#!/usr/bin/python3

from grid import *
from client import *
import socket
import sys

my_grid = grid()
my_socket = socket.socket(family=socket.AF_INET6,type=socket.SOCK_STREAM,
	proto=0, fileno=None)

def init_client():
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	my_socket.connect(('', 7777))

def main():
	while 1:
		play = 0
		message = sock.recv(5) # Should be 2 characters long
		# If it's a single digit
		if len(message) == 2 and message[0] >= 48 and message[0] <= 57:
			play = int(message)
		if play == 1:
			shot = -1
			my_grid.display()
            while shot <0 or shot >=NB_CELLS:
                shot = int(input ("A votre tour !\nQuelle case allez-vous jouer ? "))
			my_socket.send(shot)
			message = ""
			# Wait until we receive an answer 'O' or 'X' about the shot
			while len(message) == 2 and message[0] != 79 and message[0] != 88:
				message = sock.recv(5) # Should be 2 characters long
			my_grid.cells[shot] = message[0]

init_client()
main()