#!/usr/bin/python3

from grid import *
from client import *
from socket import error as SocketError
import errno
import socket
import sys
import time

my_grid = grid()
my_socket = socket.socket(family=socket.AF_INET6,type=socket.SOCK_STREAM,
	proto=0, fileno=None)

def init_client():
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	if len(sys.argv) != 2:
		print("Usage : ./client.py adresse_IP")
		exit()
	try:
		my_socket.connect((sys.argv[1], 7777))
	except socket.error:
		print("N'a pas pu se connecter. Programme avorté.")
		exit()

def game_over(message):
	while len(message) < 9: #"Game Over"
		message += my_socket.recv(1)
	print(message.decode('utf-8'))

	message = my_socket.recv(1)
	while len(message) < 9: # The moves of the game
		message += my_socket.recv(1)
	moves = message.decode('utf-8')
	for i in range(9):
		player = int(moves[i])
		my_grid.cells[i] = player
	my_grid.display()
	message = my_socket.recv(15)
	print(message.decode('utf-8'))

def main():
	game_is_over = False
	while game_is_over == False:
		play = 0
		
		try:
			message = my_socket.recv(1) # Should be 1 character long
		except SocketError as e:
			if e.errno == errno.ECONNRESET:
				exit()
			raise

		# If a character was received (if not, len() = 0)
		if len(message) == 1:
			if message[0] >= 48 and message[0] <= 57:
				play = int(message)
			elif message[0] == 71: # "Game Over"
				game_over(message)
				game_is_over = True
		if play == 1:
			print("A votre tour !")
			shot = -1
			my_grid.display()
			while shot <0 or shot >=NB_CELLS:
				try:
					shot = int(input ("Quelle case allez-vous jouer ? "))
				except ValueError:
					print("Mauvaise valeur ! Entrez un nombre de 0 à 8 !")
					time.sleep(.2)
			my_socket.send(str(shot).encode())
			message = ""
			# Wait until we receive an answer 'O' or 'X' about the shot
			while len(message) != 1:
				message = my_socket.recv(1) # Should be 1 characters long
			if (message[0] >= 48 and message[0] <= 57):
				my_grid.cells[shot] = int(message)
			elif message[0] == 71: # "Game Over"
				game_over(message)
				game_is_over = True

init_client()
main()
