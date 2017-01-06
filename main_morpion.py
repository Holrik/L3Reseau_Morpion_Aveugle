#!/usr/bin/python3

from grid import *
#from client import *
#from main import *
from socket import error as SocketError
import errno
import socket
import select
import sys



#####################################################################
###########             BEGINNING PART SERVER             ###########
#####################################################################



# Define the connection the clients will have to connect to
def init_server():
	socket_serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	socket_serv.bind(("", 7777))
	
	socket_serv.listen(1)
	list_socks.append(socket_serv)

# Add a player to the players list.
# If a player got disconnected earlier, take its Player_Number
def newplayer(sock):
	for i in range(len(players)):
		if players[i] == -1:
			players[i] = sock
			break
	players.append(sock)

# Delete a player from the players list.
# Don't remove it from the list
def delplayer(sock):
	for i in range(len(players)):
		if players[i] == sock:
			players[i] = -1
			break

# When we want to get the socket of a particular
# player (like current_player for example)
def getsock(player_num):
	return players[player_num-1]

# Get a connexion from a client
def new_client():
	new_sock, address = socket_serv.accept()
	list_socks.append(new_sock)
	newplayer(new_sock)
	if len(players) <= 2:
		message = ""
		while len(message)<1:
			message = new_sock.recv(10)
		score[len(players)-1] = int(message)
	print("New Client !")

# Send informations or a message to a player
def send_message(player, message):
	user = getsock(player)
	if user != -1:
		user.send((message).encode())
		return True
	return False # returns True if was able to deliver the message

def send_grid(grid, player):
	moves = ""
	for i in range (9):
			moves += str(grid.cells[i])
	# Send them the full grids so they can print it entirely
	send_message(player, moves)

def main_server():
	grids = [grid(), grid(), grid()]
	current_player = J1
	
	list_active_socks, a, b = select.select(list_socks, [], [])
	while len(players) < 2: # Need at least 2 players
		for active_sock in list_active_socks:
			if active_sock == socket_serv:
				new_client()
	
	while 1:
		s = send_message(current_player, "1") # His turn
		bug = False
		while s != True: # Until the message gets send(the player is connected)
			if bug == False:
				message = ("Le joueur " + str(current_player) +
					" a rencontre un probleme, veuillez patienter...")
				send_message(current_player%2+1, message)
				for i in range(3, len(players)+1):
					send_message(i, message)
				bug = True
			
			list_active_socks, a, b = select.select(list_socks, [], [])
			for active_sock in list_active_socks:
				# If someone tries to get connected
				if active_sock == socket_serv:
					new_client()
			send_message(current_player, "3")
			send_grid(grids[current_player], current_player)
			s = send_message(current_player, "1")
		shot = -1
		
		current_player_activation = False
		while current_player_activation != True:
			list_active_socks, a, b = select.select(list_socks, [], [])
			for active_sock in list_active_socks:
				# If someone tries to get connected
				if active_sock == socket_serv:
					new_client()
			
				# If the current player is doing something
				elif active_sock == getsock(current_player):
					current_player_activation = True
					# We should only receive 1 char, not more
					message = active_sock.recv(10)
					if len(message) == 1 and message[0] >= 48 and message[0] <= 57: # If it's a single digit
						shot = int(message)
						break
					# Or none if the player left
					if len(message) == 0:
						active_sock.close()
						list_socks.remove(active_sock)
						delplayer(active_sock)
						continue
				
				# If another person is doing something
				else: # Don't care about it
					message = active_sock.recv(1000)
					#Except if the client is leaving
					if len(message) == 0:
						active_sock.close()
						list_socks.remove(active_sock)
						delplayer(active_sock) # Client
						continue

		if shot < 0 or shot >= NB_CELLS: # If current_player got disconnected
			continue
			
		if grids[0].gameOver() == -1 and shot >= 0 and shot < NB_CELLS:
			# A shot has finally been made, treat it
			if (grids[0].cells[shot] != EMPTY):
				grids[current_player].cells[shot] = grids[0].cells[shot]
				send_message(current_player, str(grids[current_player].cells[shot]))
			else:
				grids[current_player].cells[shot] = current_player
				grids[0].play(current_player, shot)
				send_message(current_player, str(grids[current_player].cells[shot]))
				for i in range(3, len(players)+1):
					send_message(i, "4")
					send_message(i, str(current_player))
					send_grid(grids[0], i)
				current_player = current_player%2+1
		# Verify if it's still not a gameOver
		if grids[0].gameOver() != -1:
			break 
	# When we finally have a Game Over
	send_message(J1, "Game Over")
	if grids[0].gameOver() == J1:
	 	send_message(J1, str(score[0]+1))
	else:
		send_message(J1, str(score[0]))
	send_message(J2, "Game Over")
	if grids[0].gameOver() == J2:
		send_message(J2, str(score[1]+1))
	else:
		send_message(J2, str(score[1]))	
	for i in range(3, len(players)+1): # For the observators
		send_message(i, "Game Over")	        
	# Make the clients print the full grids
	send_grid(grids[0], J1)
	send_grid(grids[0], J2)
	if grids[0].gameOver() == J1:
		score[0] = score[0]+1
		send_message(J1, "You win !  You : " +  str(score[0]) + " | Him : " +  str(score[1]))
		send_message(J2, "You lose !  You : " +  str(score[1]) + " | Him : " +  str(score[0]))
		for i in range(3, len(players)+1):
			send_message(i, "J1 wins !  J1 : " +  str(score[0]) + " | J2 : " +  str(score[1]))
	elif grids[0].gameOver() == J2:
		score[1] = score[1]+1
		send_message(J1, "You lose !  You : " +  str(score[0]) + " | Him : " +  str(score[1]))
		send_message(J2, "You win !  You : " +  str(score[1]) + " | Him : " +  str(score[0]))
		for i in range(3, len(players)+1):
			send_message(i, "J2 wins !  J1 : " +  str(score[0]) + " | J2 : " +  str(score[1]))
	else:
		send_message(J1, "You both lose !  You : " +  str(score[0]) + " | Him : " +  str(score[1]))
		send_message(J2, "You both lose !  You : " +  str(score[1]) + " | Him : " + str(score[0]))
		for i in range(3, len(players)+1):
			send_message(i, "Everyone loses !  J1 : " + str(score[0]) + " | J2 : " + str(score[1]))



#####################################################################
###########                END PART SERVER                ###########
#####################################################################



#####################################################################
###########             BEGINNING PART CLIENT             ###########
#####################################################################



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
	try:
		my_socket.connect((sys.argv[1], 7777))
	except socket.error:
		print("N'a pas pu se connecter. Programme avorte.")
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
			main_client(point)
		

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
					print("Mauvaise valeur ! Entrez un nombre de 0 a 8 !")
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



#####################################################################
###########                END PART SERVER                ###########
#####################################################################



def main():
	print(len(sys.argv))
	if len(sys.argv) == 1: # Server, 1 argument, "./main_morpion"
		# The score of both players
		global score
		score = [0,0]
		# Necessary so we can play multiple games
		while 1:
			# Define the socket, the list of clients and the list of players
			global socket_serv
			global list_socks
			global players
			socket_serv = socket.socket(family=socket.AF_INET6,type=socket.SOCK_STREAM,
				proto=0, fileno=None)
			list_socks = []
			players = []
			init_server()
			main_server()
	elif len(sys.argv) == 2: # Client, 2 arguments, "./main_morpion host"
		point = 0
		init_client(point)
		main_client(point)
	else:
		print("Usage : ./main_morpion.py [adresse_IP]")
		exit()

main()