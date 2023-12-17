import socket
import threading
import networking

"""
Sources:
 - Python Socket Programming Tutorial - YouTube: https://www.youtube.com/watch?v=3QiPPX-KeSc
 - ChatGPT tutorials
"""

# Define constants
SERVER_ADDR = 'localhost'
PORT = 5052
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

# List to store connected clients
clients = {}


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
    print(f"Chat server is listening on {server_address[0]}:{server_address[1]}")

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
    username_set = False

    # Code will listen for data / messages from the client while they are connected
    while connected:
        try:

            # Receive the header containing the message length and decode it using the UTF-8 format
            data_length = client_socket.recv(HEADER).decode(FORMAT)
            # Parse the value to an integer
            data_length = int(data_length)

            # Receive the message data from the client using the data length received from the header
            # Blocking code - will not pass this line until data is received
            data_message = client_socket.recv(data_length).decode(FORMAT)

            # Set the clients username
            # The following code always assumes the first message is the clients username
            if not username_set:
                clients[client_socket] = data_message
                username_set = True

            # Print the message to the terminal
            print(f"[{clients[client_socket]}] {data_message}")

            # If no data received or if the disconnect message is received from the client close the connection
            if not data_message or data_message == '!DISCONNECT':
                connected = False

            # Broadcast the message to all clients
            networking.broadcast(data_message, client_socket, clients, HEADER)

        except Exception as e:
            print(f"Error: {e}")
            break

    # Remove the client from the list and close the connection
    print(f"[REMOVE CLIENT] {clients[client_socket]}")
    del clients[client_socket]
    client_socket.close()


while application_running:
    command = input('Enter a command: ')

    if command == 'server-start':
        start_server()
    elif command == 'server-stop':
        stop_server()
    elif command == 'quit':
        break
    else:
        print('Please enter a valid command')



