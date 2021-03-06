#!/usr/bin/python3

from grid import *
from client import *
from main import *
from socket import error as SocketError
import errno
import socket
import sys

# Gets a connection with the server if possible. If not possible, exit
def init_client(point):
	continuer = ""
	while continuer != "y":
		try:
			continuer = input ("Voulez vous jouer en ligne? y/n :")
		except ( EOFError):
		# If the value is an End Of File (error)
			print("Mauvaise valeur ! Entrez y ou n !")
			time.sleep(.2)
		if continuer != "n" and continuer != "y":
			print("Mauvaise valeur ! Entrez y ou n !")
			time.sleep(.2)
		else:
			if continuer == "n":
				print("Joueur contre l'IA")
				main()
				init_client(point)

	print("Joueur contre Joueur")
	global my_socket
	global my_grid
	my_grid = grid()
	my_socket = socket.socket(family=socket.AF_INET6,type=socket.SOCK_STREAM,
		proto=0, fileno=None)
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	if len(sys.argv) != 2:
		print("Usage : ./client.py adresse_IP")
		exit()
	try:
		my_socket.connect((sys.argv[1], 7777))
	except socket.error:
		print("N'a pas pu se connecter. Programme avorté.")
		exit()
	my_socket.send(str(point).encode())	

# To receive the full state of the grid from the server
def receive_grid():
	message = my_socket.recv(1)
	while len(message) < 9: # The moves of the game
		message += my_socket.recv(1)
	moves = message.decode('utf-8')
	for i in range(9):
		player = int(moves[i])
		my_grid.cells[i] = player

# Receive the necessary informations to print when the game is over
def game_over(message, observateur,point):
	continuer = ""
	while len(message) < 9: #"Game Over"
		message += my_socket.recv(1)
	print(message.decode('utf-8'))
	if observateur == 0: # observateur = False
		message = ""
		while len(message) < 1:
			message = my_socket.recv(1)
                    
		point = int(message)       
	if observateur == 0:
		receive_grid()
		my_grid.display()
	
	message = my_socket.recv(30) # Winner/Loser
	print(message.decode('utf-8'))
	my_socket.close()
	while continuer != "y":
		try:
			continuer = input ("Voulez vous rejouer une partie ? y/n :")
		except ( EOFError):
		# If the value is anything but an int
			print("Mauvaise valeur ! Entrez y ou n !")
			time.sleep(.2)
		if continuer != "n" and continuer != "y":
			print("Mauvaise valeur ! Entrez y ou n !")
			time.sleep(.2)
		else:
			if continuer == "n":
				exit()
			init_client(point)
			client(point)
		

# Play the game
def main_client(point):
	observateur = 0
	while 1:
		action = 0
		
		message = ""
		try:
			message = my_socket.recv(1) # Should be 1 character long
		except SocketError as e:
			# If the connection's been reset for some reason
			if e.errno == errno.ECONNRESET:
				exit()
			# If another exception was raised, don't care
			raise 

		# If a character was received, means the server has been disconnected
		if len(message) == 0:
			print("Le serveur a rencontre un probleme, deconnection...")
			exit()
		if len(message) == 1:
			if message[0] >= 48 and message[0] <= 57:
			    action = int(message)
			elif message[0] == 71: # "G" for "Game Over"
			    action = 2
			else:
				message += my_socket.recv(99)
				print(message.decode())
		
		# If we received the signal for us to make a move
		if action == 1:
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
			    action = 2
			else:
				message += my_socket.recv(99)
				print(message.decode())

		if action == 2: # Game Over                
			game_over(message, observateur,point)            

		# If we received the signal for us to receive the grid
		if action == 3: # After reconnexion
			receive_grid()
		if action == 4: # As an observator
			observateur = 1
			message = my_socket.recv(1) # The ID of the player who just played
			print("Le joueur " + message.decode() + " vient de jouer :")
			receive_grid()
			my_grid.display()

point = 0
init_client(point)
main_client(point)
