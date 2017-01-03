#!/usr/bin/python3

from grid import *
import socket
import select

# Define the socket, the list of clients and the list of players
socket_serv = socket.socket(family=socket.AF_INET6,type=socket.SOCK_STREAM,
	proto=0, fileno=None)
list_socks = []
players = []

# Define the connection the clients will have to connect to
def init_server():
	socket_serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	socket_serv.bind(('', 7777))
	
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

def main():
	grids = [grid(), grid(), grid()]
	current_player = J1
	
	list_active_socks, a, b = select.select(list_socks, [], [])
	while len(players) < 2: # Need at least 2 players
		for active_sock in list_active_socks:
			if active_sock == socket_serv:
				new_client()
	
	while 1:
		s = send_message(current_player, "1") # His turn
		while s != True: # Until the message gets send(the player is connected)
			list_active_socks, a, b = select.select(list_socks, [], [])
			for active_sock in list_active_socks:
				# If someone tries to get connected
				if active_sock == socket_serv:
					new_client()
			send_message(current_player, "3")
			send_grid(grids[current_player], current_player)
			s = send_message(current_player, "1")
		shot = -1
		
		list_active_socks, a, b = select.select(list_socks, [], [])
		for active_sock in list_active_socks:
			# If someone tries to get connected
			if active_sock == socket_serv:
				new_client()
			
			# If the current player is doing something
			elif active_sock == getsock(current_player):
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

		if shot < 0 or shot >= NB_CELLS:
			send_message(current_player%2+1, "Le joueur " + str(current_player) +
				" a rencontre un probleme, veuillez patienter...")
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
				current_player = current_player%2+1
		# Verify if it's still not a gameOver
		if grids[0].gameOver() != -1:
			break #To adjust later if we want to play multiple times
	send_message(J1, "Game Over")
	send_message(J2, "Game Over")

	grids[0].display()
	# Print the full grids
	send_grid(grids[0], J1)
	send_grid(grids[0], J2)

	if grids[0].gameOver() == J1:
		send_message(J1, "You win !")
		send_message(J2, "You lose !")
	elif grids[0].gameOver() == J2:
		send_message(J1, "You lose !")
		send_message(J2, "You win !")
	else:
		send_message(J1, "You lose !")
		send_message(J2, "You lose !")

init_server()
main()
