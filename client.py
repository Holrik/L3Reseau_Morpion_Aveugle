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
		message = my_socket.recv(1) # Should be 1 character long
		# If it's a single 
		if len(message) == 1:
			if message[0] >= 48 and message[0] <= 57:
				play = int(message)
			else:
				message += my_socket.recv(19)
				print(message)
		if play == 1:
			shot = -1
			my_grid.display()
			while shot <0 or shot >=NB_CELLS:
				shot = int(input ("A votre tour !\nQuelle case allez-vous jouer ? "))
			my_socket.send(str(shot).encode())
			message = ""
			# Wait until we receive an answer 'O' or 'X' about the shot
			while len(message) != 1:
				message = my_socket.recv(1) # Should be 1 characters long
			if (message[0] >= 48 and message[0] <= 57):
				my_grid.cells[shot] = int(message)
			else: # game over
				message += my_socket.recv(8)
				print(message.decode('utf-8'))
				my_grid.display()
				message = my_socket.recv(10)
				print(message)

init_client()
main()
