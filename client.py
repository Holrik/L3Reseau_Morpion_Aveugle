#!/usr/bin/python3

from grid import *
from client import *
from socket import error as SocketError
import errno
import socket
import sys
import time

# Define the user's grid and the socket
my_grid = grid()
my_socket = socket.socket(family=socket.AF_INET6,type=socket.SOCK_STREAM,
	proto=0, fileno=None)

# Gets a connection with the server if possible. If not possible, exit
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

def receive_grid():
	message = my_socket.recv(1)
	while len(message) < 9: # The moves of the game
		message += my_socket.recv(1)
	moves = message.decode('utf-8')
	for i in range(9):
		player = int(moves[i])
		my_grid.cells[i] = player

# Receive the necessary informations to print when the game is over
def game_over(message):
	while len(message) < 9: #"Game Over"
		message += my_socket.recv(1)
	print(message.decode('utf-8'))
    
	receive_grid()
	my_grid.display()
	
	message = my_socket.recv(15) # You win/lose
	print(message.decode('utf-8'))

# Play the game
def main():
	game_is_over = False
	while game_is_over == False:
		play = 0
		
		message = ""
		try:
			message = my_socket.recv(1) # Should be 1 character long
		except SocketError as e:
			# If the connection's been reset for some reason
			if e.errno == errno.ECONNRESET:
				exit()
			# If another exception was raised, don't care
			raise 

		# If a character was received (if not, len() = 0)
		if len(message) == 0:
			print("Le serveur a rencontre un probleme, deconnection...")
			exit()
		if len(message) == 1:
			if message[0] >= 48 and message[0] <= 57:
				play = int(message)
			elif message[0] == 71: # "G" for "Game Over"
				game_over(message)
				game_is_over = True
			else:
				message += my_socket.recv(99)
				print(message.decode())
		
		# If we received the signal for us to make a move
		if play == 1:
			print("A votre tour !")
			shot = -1
			my_grid.display()
			
			# Wait until the player plays
			while shot <0 or shot >=NB_CELLS:
				try:
					shot = int(input ("Quelle case allez-vous jouer ? "))
				except (ValueError, EOFError):
					# If the value is anything but an int
					print("Mauvaise valeur ! Entrez un nombre de 0 à 8 !")
					time.sleep(.2)
			
			# shot now has a valid value, we can send it to the server
			my_socket.send(str(shot).encode())
			
			# Wait until we receive an answer 'O' or 'X' about the shot
			message = my_socket.recv(1) # Should be 1 character long
			if len(message) == 0:
				print("Le serveur a rencontre un probleme, deconnection...")
				exit()
			
			# Check if the answer was a digit (1 = 'O', 2 = 'X')
			if (message[0] >= 48 and message[0] <= 57):
				my_grid.cells[shot] = int(message)
			elif message[0] == 71: # "G" for "Game Over"
				game_over(message)
				game_is_over = True
			else:
				message += my_socket.recv(99)
				print(message.decode())

		# If we received the signal for us to receive the grid
		if play == 3:
			receive_grid()
init_client()
main()
