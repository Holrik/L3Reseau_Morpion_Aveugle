#!/usr/bin/python3

from grid import *
import socket
import select

socket_serv = socket.socket(family=socket.AF_INET6,type=socket.SOCK_STREAM,
	proto=0, fileno=None)
list_socks = []
players = []

def init_server():
	socket_serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	socket_serv.bind(('', 7777))
	
	socket_serv.listen(1)
	list_socks.append(socket_serv)

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

def getsock(player_num):
	return players[player_num-1]

def new_client():
	new_sock, address = socket_serv.accept()
	list_socks.append(new_sock)
	newplayer(new_sock)

def send_message(player, message):
	user = getsock(player)
	user.send((message).encode())

def main():
	grids = [grid(), grid(), grid()]
	current_player = J1
	
	list_active_socks, a, b = select.select(list_socks, [], [])
	while len(players) < 2: # Need at least 2 players
		for active_sock in list_active_socks:
			if active_sock == socket_serv:
				new_client()
	
	while 1:
		send_message(current_player, "1") # His turn
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
				# Or none if the player left
				if len(message) == 0:
					active_sock.close()
					list_socks.remove(active_sock)
					delplayer(active_sock)
					continue
				if len(message) == 1 and message[0] >= 48 and message[0] <= 57: # If it's a single digit
					shot = int(message)
					break
				
			# If another person is doing something
			else: # Don't care about it
				message = active_sock.recv(1000)
				#Except if the client is leaving
				if len(message) == 0:
					active_sock.close()
					list_socks.remove(active_sock)
					delplayer(active_sock) # Client
					continue
		
		if grids[0].gameOver() == -1:
			# A shot has finally been made
			if (grids[0].cells[shot] != EMPTY):
				grids[current_player].cells[shot] = grids[0].cells[shot]
				send_message(current_player, str(grids[current_player].cells[shot]))
#				print(str(grids[current_player].cells[shot]))
			else:
				grids[current_player].cells[shot] = current_player
				grids[0].play(current_player, shot)
				send_message(current_player, str(grids[current_player].cells[shot]))
				current_player = current_player%2+1
		else:
			break #To adjust later if we want to play multiple times
	send_message(J1, "game over")
	send_message(J2, "game over")
	grids[0].display()
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
