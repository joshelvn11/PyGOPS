import socket
import time
import networking

# Define Constants
HEADER = 64
FORMAT = "utf-8"
SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 7020

# Define global variables
game_id = ""


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


def print_slowly(text, new_line=True, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)

    if new_line:
        print('')


# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
print_slowly('Enter server IP (leave blank for default): ', False)
server_ip_input = input()
if server_ip_input:
    SERVER_ADDR = server_ip_input

print_slowly('Enter server port (leave blank for default): ', False)
server_port_input = input()
if server_port_input:
    SERVER_PORT = int(server_port_input)

server_address = (SERVER_ADDR, SERVER_PORT)
client_socket.connect(server_address)

# Wait for successful connection response
receive_response()

# Send the clients username to the server
print_slowly("Please choose a name to play with: ", False)
username = input()
message = f"SET-USERNAME~{username}"
networking.send_message(message, client_socket, HEADER)

# Wait for response that set username has been successful
receive_response()


# Start game procedure
def create_join_game_procedure():

    global game_id

    # Ask if the client would like to create a game or connect to an existing game
    print_slowly("Would you like to [1] create a game [2] connect to a game: ", False)
    start_game = input()

    if start_game == '1':
        message_response = f"START-GAME~{start_game}"
        networking.send_message(message_response, client_socket, HEADER)

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
        message_response = f"JOIN-GAME~{input_game_id}"
        networking.send_message(message_response, client_socket, HEADER)

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
            message_response = input()
            message_response = f"PLAY-TURN~{game_id}${message_response}"
            networking.send_message(message_response, client_socket, HEADER)

        elif response_command == "END-GAME":
            pass

        elif response_command == "CLOSE-GAME":
            pass

        # Continue to the next iteration of the loop and listen for another message if it is an info message
        elif response_command == 'INFO':
            continue


game_play_procedure()
