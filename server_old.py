import socket
import threading
import networking
import game
import sys

"""
Sources:
 - Python Socket Programming Tutorial - YouTube: https://www.youtube.com/watch?v=3QiPPX-KeSc
 - ChatGPT tutorials
"""

# Define constants
SERVER_ADDR = 'localhost'
PORT = 5059
ADDR = (SERVER_ADDR, PORT)
HEADER = 64
FORMAT = 'utf-8'

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_address = (SERVER_ADDR, PORT)
server_socket.bind(server_address)

# Variable to track the application state
application_running = True

# Variable to track the server state
server_running = True

# Dictionary to store connected clients
clients = {}

# Dictionary to store active games
active_games = {}

# ---------- FUNCTION DEFINITIONS -----


# Function to start the server
def start_server():
    print('Starting server...')

    global server_running
    server_running = True
    server_thread = threading.Thread(target=server_worker)
    server_thread.start()


# Function to shut down the server and close all sockets
def stop_server():

    print('Stopping server...')

    global server_running
    server_running = False

    # Close all client connections
    for client_socket in clients.values():
        client_socket[0].close()

    # Close the server socket
    server_socket.close()

    print('Server stopped...')


# Server worker to be run as independent thread. Listens for connection requests and
# starts threads to handle clients
def server_worker():

    print('Server started...')

    # Listen for incoming connections
    server_socket.listen()
    print(f"[SERVER-STARTED] Listening on {server_address[0]}:{server_address[1]}")

    while server_running:

        # Accept a connection
        # Get the client socket object and client address and assign to variables
        client_socket, client_address = server_socket.accept()  # Blocking code
        print(f"[NEW CONNECTION] {client_address}")

        # Add the new client to the dict with a default username
        clients[client_socket] = [client_socket, client_address, f"User: {len(clients)}"]

        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

        # List the active threads / connections
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


# Function to handle individual clients and listen for messages from each client
def handle_client(client_socket):

    connected = True

    # Code will listen for data / messages from the client while they are connected
    while connected:
        try:

            # Receive the header containing the message length and decode it using the UTF-8 format
            data_length = client_socket.recv(HEADER).decode(FORMAT)

            # Only attempt to handle the message if it has data (i.e the header is not empty)
            if data_length:

                # Parse the value to an integer
                data_length = int(data_length)

                # Receive the message data from the client using the data length received from the header
                # Blocking code - will not pass this line until data is received
                data_message = client_socket.recv(data_length).decode(FORMAT)

                # Print the message to the terminal
                print(f"[{client_socket}] {data_message}")

                # Split the string into the command and message content
                message_command = data_message.split('~')[0]
                message_body = data_message.split('~')[1]

                # Process the command and message
                if message_command == 'SET-USERNAME':
                    clients[client_socket][2] = message_body
                    message_response = f"[SUCCESS] Username set to {clients[client_socket]} successfully"
                    networking.send_message(message_response, client_socket, HEADER)
                    print(f"[RESPONSE TO CLIENT] {message_response}")
                elif message_command == 'START-GAME':
                    if message_body == '1':
                        print("[STARTING GAME]")
                        message_response = f"[STARTING NEW GAME]"
                        networking.send_message(message_response, client_socket, HEADER)
                        print(f"[RESPONSE TO CLIENT] {message_response}")
                        game_instance = game.Game(self)

                # If no data received or if the disconnect message is received from the client close the connection
                if not data_message or data_message == '!DISCONNECT':
                    connected = False

                # Broadcast the message to all clients
                # networking.broadcast(data_message, client_socket, clients, HEADER)

        except Exception as e:
            print(f"Error: {e}")
            break

    # Remove the client from the list and close the connection
    # clients.remove(client_socket)
    client_socket.close()


# ---------- APPLICATION LOGIC -----

start_server()

while application_running:
    command = input('$: ')

    if command == 'server-start':
        start_server()
    elif command == 'server-stop':
        stop_server()
    elif command == 'quit':
        break
    elif command == 'active-clients':
        print("List of currently active clients:")
        for client in clients.values():
            print(client)
    elif command == 'active-clients-sockets':
        for client in clients.values():
            print(client[0])
    elif command == 'active-clients-addresses':
        for client in clients.values():
            print(client[1])
    elif command == 'active-clients-usernames':
        print("List of currently active client usernames:")
        for client in clients.values():
            print(client[2])
    elif command == 'active-games':
        pass
    else:
        print('Please enter a valid command')



