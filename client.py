import socket
import time
import threading
import pickle

HEADER = 64
FORMAT = 'utf-8'

game_id = ""

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
        # print(f"[HEADER] {data_length}")
        if data_length == '':
            data_length = 1024
            print("[WARNING] Blank header received, setting message buffer to 1024 bytes")
        data_length = int(data_length)

        # Receive the message data from the server using the data length received from the header
        # Blocking code - will not pass this line until data is received
        data_message = client_socket.recv(data_length).decode(FORMAT)

        # print(f"[MSG] {data_message}")

        # Split the string into the command and message content
        message_command = data_message.split('~')[0]
        message_body = data_message.split('~')[1]

        # Print info message directly to the console
        if message_command == 'INFO':
            print_slowly(message_body)

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


def print_slowly(text, new_line=True, delay=0.05):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)

    if new_line:
        print('')

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
# server_ip = input('Please enter the server IP you would like to connect to: ')
# server_port = input('Please enter the port to connect with')
server_address = ('localhost', 5079)
client_socket.connect(server_address)

# Send the clients username to the server
print_slowly("Please choose a name to connect with: ", False)
username = input()
message = f"SET-USERNAME~{username}"
send_message(message)

# Wait for response that set username has been successful
receive_response()


# Start game procedure
def create_join_game_procedure():

    global game_id

    # Ask if the client would like to create a game or connect to an existing game
    print_slowly("Would you like to [1] create a game [2] connect to a game: ", False)
    start_game = input()

    if start_game == '1':
        message = f"START-GAME~{start_game}"
        send_message(message)

        # Wait for response that server has received start new game command
        receive_response()

        # Wait for response that new game has been started
        receive_response()

        # Wait for the game ID and set the global game ID
        response_command, response_body = receive_response()
        if response_command == 'SET-ID':
            game_id = response_body
        else:
            print("[ERROR] Invalid response from server, expected game ID")
            print(f"[ERROR INFO] Response received: '{response_command, response_body}'")

    elif start_game == '2':
        print_slowly("Please enter the ID of the game you wish to join: ", False)
        input_game_id = input()
        message = f"JOIN-GAME~{input_game_id}"
        send_message(message)

        # Wait for response if joining the game was successful
        response_command, response_body = receive_response()

        if response_command == 'TRUE':
            print_slowly(response_body)

            # Wait for the game ID and set the global game ID
            response_command, response_body = receive_response()
            if response_command == 'SET-ID':
                game_id = response_body
            else:
                print("[ERROR] Invalid response from server, expected game ID")
        elif response_command == 'FALSE':
            print(response_body)
            create_join_game_procedure()

    else:
        print_slowly("Please enter a valid option.")
        create_join_game_procedure()


create_join_game_procedure()


def game_play_procedure():

    game_in_play = True

    while game_in_play:

        response_command, response_body = receive_response()

        if response_command == "YOUR-TURN":
            print_slowly(response_body, False)
            message = input()
            message = f"PLAY-TURN~{game_id}${message}"
            send_message(message)

        elif response_command == "END-GAME":
            pass

        elif response_command == "CLOSE-GAME":
            pass

        # Continue to the next iteration of the loop and listen for another message if it is an info message
        elif response_command == 'INFO':
            continue


# Wait to receive the start game command
# while True:
#
#     response_command, response_body = receive_response()
#
#     if response_command == "START-GAME":
#         print(response_body)
#         break

# Start the game_play procedure
game_play_procedure()


# Start a thread to receive messages from the server
# receive_thread = threading.Thread(target=receive_messages)
# receive_thread.start()
