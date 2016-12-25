#!/usr/bin/python3

from grid import *
import socket
import select

socket_serv
list_clients = []

def init_server():
	socket_serv = socket.socket(family=socket.AF_INET6,type=socket.SOCK_STREAM,
              proto=0, fileno=None)
	socket_serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	socket_serv.bind(('', 7777))

	socket_serv.listen(1)
	list_clients.append(socket_serv)



def main():
    grids = [grid(), grid(), grid()]
	list_players = [J1, J2]
    current_player = J1
    while grids[0].gameOver() == -1:
		turn_start = True
		shot = -1
		while shot <0 or shot >=NB_CELLS:
			if turn_start == True and client.is_connected(current_player):
				client.display_grid(current_player)
				message = "A votre tour !\nQuelle case allez-vous jouer ?"
				send_message(current_player, message)
            
			list_active_socks, a, b = select.select(list_clients, [], [])
			for active_sock in list_active_socks:
				# If the server is doing something
				if active_sock == socket_serv:
					new_client(list_clients, active_sock)
					
				# If the current player is doing something
				elif active_sock == client.getsock(current_player):
					message = active_sock.recv(10) # Should only receive 1 char
					shot = int(message)
					
				# If another person is doing something
				else: # Don't care about it
					active_sock.recv(1000)
				
		# A shot has finally been made
        if (grids[0].cells[shot] != EMPTY):
            grids[current_player].cells[shot] = grids[0].cells[shot]
        else:
            grids[current_player].cells[shot] = current_player
            grids[0].play(current_player, shot)
            current_player = current_player%2+1
        if current_player == J1:
            grids[J1].display()
    send_message(J1, "game over")
    send_message(J2, "game over")
	client.display_grid(J1)
	client.display_grid(J2)
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
