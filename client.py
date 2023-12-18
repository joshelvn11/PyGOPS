import socket
import threading
import pickle

HEADER = 64
FORMAT = 'utf-8'


# Function to continually listen for messages
def receive_messages():
    while True:
        try:
            # Receive the header containing the message length and decode it using the UTF-8 format
            data_length = client_socket.recv(HEADER).decode(FORMAT)
            # Parse the value to an integer
            data_length = int(data_length)

            # Receive the message data from the server using the data length received from the header
            # Blocking code - will not pass this line until data is received
            data_message = client_socket.recv(data_length).decode(FORMAT)

            print(data_message)

        except:
            print("Connection lost.")
            break


# Function to listen for a single message
def receive_response():
    try:

        # Receive the header containing the message length and decode it using the UTF-8 format
        data_length = client_socket.recv(HEADER).decode(FORMAT)
        # Parse the value to an integer
        data_length = int(data_length)

        # Receive the message data from the server using the data length received from the header
        # Blocking code - will not pass this line until data is received
        data_message = client_socket.recv(data_length).decode(FORMAT)

        print(data_message)

    except:
        print("Connection lost.")


def send_message(data_message):

    # Encode the message data
    data_message = data_message.encode()

    # Serialize the message object for sending
    # data_message = pickle.dumps(data_message)

    # Determine the message data length to create the message header
    data_length = len(data_message)

    # Encode the data length to send
    data_length = str(data_length).encode()

    # Pad the data length to make it 64 bytes
    data_length += b' ' * (HEADER - len(data_length))

    # Send the data length (header) to the server
    client_socket.send(data_length)

    # Send the message data to the server
    client_socket.send(data_message)


# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
# server_ip = input('Please enter the server IP you would like to connect to: ')
# server_port = input('Please enter the port to connect with')
server_address = ('localhost', 5058)
client_socket.connect(server_address)

# Start a thread to receive messages from the server
# receive_thread = threading.Thread(target=receive_messages)
# receive_thread.start()

# Send the clients username to the server
username = input("Please choose a name to connect with: ")
message = f"SET-USERNAME~{username}"
send_message(message)

receive_response()

# Ask if the client would like to create a game or connect to an existing game
start_game = input("Would you like to [1] connect to a game or [2] create a game: ")
message = f"START-GAME~{start_game}"
send_message(message)

receive_response()




