import socket
import threading

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_address = ('localhost', 5555)
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen(5)
print(f"Chat server is listening on {server_address[0]}:{server_address[1]}")

# List to store connected clients
clients = []

# Variable to track the application state
application_running = True

# Variable to track the server state
server_running = True


def handle_client(client_socket):
    while True:
        try:
            # Receive data from the client
            data = client_socket.recv(1024).decode()
            if not data:
                break  # If no data received, break the loop

            # Check if the command is to shut down the server
            if data == "/shutdown":
                server_socket.close()
                print("Server shutting down...")
                global server_running
                server_running = False
                break

            # Broadcast the message to all clients
            broadcast(data, client_socket)
        except Exception as e:
            print(f"Error: {e}")
            break

    # Remove the client from the list and close the connection
    clients.remove(client_socket)
    client_socket.close()


def broadcast(message, sender_socket):

    for client in clients:
        try:
            # Send the message to all other clients
            client.send(message.encode())
        except:
            # If sending fails, remove the client from the list
            clients.remove(client)


def server_worker():
    while server_running:
        # Accept a connection
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        # Add the new client to the list
        clients.append(client_socket)

        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


def start_server():
    print('Starting server...')

    global server_running
    server_running = True
    server_thread = threading.Thread(target=server_worker)

    print('Server started...')


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


while application_running:
    command = input('Enter a command:')

    if command == 'server-start':
        start_server()
    elif command == 'server-stop':
        stop_server()
    elif command == 'quit':
        pass
    else:
        print('Please enter a valid command')



