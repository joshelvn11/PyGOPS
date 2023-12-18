import socket
import threading
import networking
import sys

"""
Sources:
 - Python Socket Programming Tutorial - YouTube: https://www.youtube.com/watch?v=3QiPPX-KeSc
 - ChatGPT tutorials
"""

# Define constants
SERVER_ADDR = 'localhost'
PORT = 5058
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
games = {}


def start_server():
    print('Starting server...')

    global server_running
    server_running = True
    server_thread = threading.Thread(target=server_worker)
    server_thread.start()


def stop_server():

    print('Stopping server...')

    global server_running
    server_running = False

    # Close all client connections
    for client_socket in clients:
        client_socket.close()

    # Close the server socket
    server_socket.close()

    print('Server stopped...')


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
        clients[client_socket] = f"User: {len(clients)}"

        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

        # List the active threads / connections
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


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
                    clients[client_socket] = message_body
                    message_response = f"[SUCCESS] Username set to {clients[client_socket]} successfully"
                    networking.send_message(message_response, client_socket, HEADER)
                    print(f"[RESPONSE TO CLIENT] {message_response}")
                elif message_command == 'START-GAME':
                    if message_body == '1':
                        print("[STARTING GAME]")
                        message_response = f"[STARING NEW GAME]"
                        networking.send_message(message_response, client_socket, HEADER)
                        print(f"[RESPONSE TO CLIENT] {message_response}")

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


# def handle_client(client_socket):
#
#     connected = True
#     username_set = False
#
#     # Code will listen for data / messages from the client while they are connected
#     while connected:
#         try:
#
#             # Receive the header containing the message length and decode it using the UTF-8 format
#             data_length = client_socket.recv(HEADER).decode(FORMAT)
#
#             # Parse the value to an integer
#             data_length = int(data_length)
#             print(f"[HEADER] {data_length}")
#
#             # Receive the message data from the client using the data length received from the header
#             # Blocking code - will not pass this line until data is received
#             data_message = client_socket.recv(1024).decode(FORMAT)
#             print(f"[{clients[client_socket]}] {data_message}")
#
#             # Split the string into the command and message content
#             message_command = data_message.split('~')[0]
#             message_body = data_message.split('~')[1]
#
#             # Process the command and message
#             if message_command == 'SET-USERNAME':
#                 clients[client_socket] = message_body
#                 message_response = f"[SUCCESS] Username set to {clients[client_socket]} successfully"
#                 message_response = message_response.encode()
#                 client_socket.send(message_response)
#
#             # Print the message to the terminal
#             print(f"[{clients[client_socket]}] {data_message}")
#
#             # If no data received or if the disconnect message is received from the client close the connection
#             if not data_message or data_message == '!DISCONNECT':
#                 connected = False
#
#             # Broadcast the message to all clients
#             # networking.broadcast(data_message, client_socket, clients, HEADER)
#
#         except Exception as e:
#             print(f"Error: {e}")
#             exception_type, exception_instance, traceback = sys.exc_info()
#             print(f"Caught exception of type: {exception_type.__name__}")
#             print(f"Exception instance: {exception_instance}")
#             break
#
#     # Remove the client from the list and close the connection
#     print(f"[REMOVE CLIENT] {clients[client_socket]}")
#     del clients[client_socket]
#     client_socket.close()


start_server()

while application_running:
    command = input('$: ')

    if command == 'server-start':
        start_server()
    elif command == 'server-stop':
        stop_server()
    elif command == 'quit':
        break
    else:
        print('Please enter a valid command')



