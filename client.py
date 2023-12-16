import socket
import threading

def receive_messages():
    while True:
        try:
            # Receive and print messages from the server
            message = client_socket.recv(1024).decode()
            print(message)
        except:
            print("Connection lost.")
            break


# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('localhost', 5050)
client_socket.connect(server_address)

# Start a thread to receive messages from the server
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Send messages to the server
while True:
    message = input('Enter message: ')
    client_socket.send(message.encode())
