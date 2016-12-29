#!/usr/bin/python3

from grid import *
from client import *
import socket
import select

socket_serv = socket.socket(family=socket.AF_INET6,type=socket.SOCK_STREAM,
	proto=0, fileno=None)
list_socks = []

def init_server():
	socket_serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	socket_serv.bind(('', 7777))
	
	socket_serv.listen(1)
	list_socks.append(socket_serv)


def new_client():
	new_sock, address = socket_serv.accept()
	list_socks.append(new_sock)
	newplayer(new_sock) # Client

def send_message(player, message):
	user = getsock(player) # Client
	user.send((message+"\n").encode())

def main():
	grids = [grid(), grid(), grid()]
	list_players = [J1, J2]
	players_connected = 0
	current_player = J1
	
	list_active_socks, a, b = select.select(list_socks, [], [])
	while players_connected < 2:
		for active_sock in list_active_socks:
			if active_sock == socket_serv:
				new_client()
				players_connected += 1
	
	while 1:
		shot = -1
		
		display_grid(current_player, grids[current_player]) # Client
		message = "A votre tour !\nQuelle case allez-vous jouer ?"
		send_message(current_player, message)
		
		while shot <0 or shot >=NB_CELLS:
			list_active_socks, a, b = select.select(list_socks, [], [])
			for active_sock in list_active_socks:
				# If someone tries to get connected
				if active_sock == socket_serv:
					new_client()
				
				# If the current player is doing something
				elif active_sock == getsock(current_player): # Client
					# We should only receive 1 char, not more
					message = active_sock.recv(10)
					# Or none if the player left
					if len(message) == 0:
						active_sock.close()
						list_socks.remove(active_sock)
						delplayer(active_sock) # Client
						continue
					if len(message) == 2 and message[0] >= 48 and message[0] <= 57: # If it's a single digit
						shot = int(message)
					
				# If another person is doing something
				else: # Don't care about it
					active_sock.recv(1000)
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
			else:
				grids[current_player].cells[shot] = current_player
				grids[0].play(current_player, shot)
				current_player = current_player%2+1
		else:
			break #To adjust later if we want to play multiple times
	send_message(J1, "game over")
	send_message(J2, "game over")
	display_grid(J1, grids[J1]) # Client
	display_grid(J2, grids[J2]) # Client
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
