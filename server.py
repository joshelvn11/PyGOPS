import socket
import threading

"""
Sources:
 - Python Socket Programming Tutorial - YouTube: https://www.youtube.com/watch?v=3QiPPX-KeSc
 - ChatGPT tutorials
"""

# Define constants
SERVER_ADDR = 'localhost'
PORT = 5050
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
clients = []


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
    server_socket.listen(5)
    print(f"Chat server is listening on {server_address[0]}:{server_address[1]}")

    while server_running:

        # Accept a connection
        # Get the client socket object and client address and assign to variables
        client_socket, client_address = server_socket.accept()  # Blocking code
        print(f"[NEW CONNECTION] {client_address}")

        # Add the new client to the list
        clients.append(client_socket)

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
            # Parse the value to an integer
            data_length = int(data_length)

            # Receive the message data from the client using the data length received from the header
            # Blocking code - will not pass this line until data is received
            data_message = client_socket.recv(data_length).decode(FORMAT)

            # Print the message to the terminal
            print(f"[{client_socket}] {data_message}")

            # If no data received or if the disconnect message is received from the client close the connection
            if not data_message or data_message == '!DISCONNECT':
                connected = False

            # Broadcast the message to all clients
            broadcast(data_message, client_socket)

        except Exception as e:
            print(f"Error: {e}")
            break

    # Remove the client from the list and close the connection
    clients.remove(client_socket)
    client_socket.close()


def broadcast(data_message, sender_socket):
    # Encode the message data
    data_message = data_message.encode()

    # Determine the message data length to create the message header
    data_length = len(data_message)

    # Encode the data length to send
    data_length = str(data_length).encode()

    # Pad the data length to make it 64 bytes
    data_length += b' ' * (HEADER - len(data_length))

    for client in clients:
        try:
            # Send the data length (header) to the client
            client.send(data_length)

            # Send the message data to the client
            client.send(data_message)
        except:
            # If sending fails, remove the client from the list
            clients.remove(client)


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



