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

        # Split the string into the command and message content
        message_command = data_message.split('~')[0]
        message_body = data_message.split('~')[1]

        # Print info message directly to the console
        if message_command == 'INFO':
            print(message_body)

        return message_command, message_body

    except Exception as e:
        print(f"[ERROR] Error in receive_response()")
        print(f"[ERROR INFO] {e}")


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
server_address = ('localhost', 5073)
client_socket.connect(server_address)

# Send the clients username to the server
username = input("Please choose a name to connect with: ")
message = f"SET-USERNAME~{username}"
send_message(message)

# Wait for response that set username has been successful
receive_response()


# Start game procedure
def create_join_game_procedure():
    # Ask if the client would like to create a game or connect to an existing game
    start_game = input("Would you like to [1] create a game [2] connect to a game: ")

    if start_game == '1':
        message = f"START-GAME~{start_game}"
        send_message(message)

        # Wait for response that server has received start new game command
        receive_response()

        # Wait for response that new game has been started and the game ID
        receive_response()

    elif start_game == '2':
        game_id = input("Please enter the ID of the game you wish to join: ")
        message = f"JOIN-GAME~{game_id}"
        send_message(message)

        # Wait for response if joining the game was successful
        response_command, response_body = receive_response()

        if response_command == 'TRUE':
            print(response_body)
        elif response_command == 'FALSE':
            print(response_body)
            create_join_game_procedure()

    else:
        print("Please enter a valid option.")
        create_join_game_procedure()


create_join_game_procedure()


def game_play_procedure():

    game_in_play = True

    while game_in_play:

        response_command, response_body = receive_response()

        if response_command == "YOUR-TURN":
            input(f"{response_body}: ")

        elif response_command == "END-GAME":
            pass

        elif response_command == "CLOSE-GAME":
            pass

        # Continue to the next iteration of the loop and listen for another message if it is an info message
        elif response_command == 'INFO':
            continue


# Wait to receive the start game command
while True:

    response_command, response_body = receive_response()

    if response_command == "START-GAME":
        print(response_body)
        break

# Start the game_play procedure
game_play_procedure()


# Start a thread to receive messages from the server
# receive_thread = threading.Thread(target=receive_messages)
# receive_thread.start()
