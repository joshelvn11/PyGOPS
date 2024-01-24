import socket
import time
import networking

# Define Constants
HEADER = 64
FORMAT = "utf-8"
SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 6070

# Define global variables
game_id = ""
client_socket = None


def receive_response():
    """
    When called this function waits to receive a single response and processes it accordingly.
    This function is run on the main thread meaning it blocks the script from proceeding until
    a response has been received.
    :return:
    """
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
    """
    Prints text to the terminal character by character with the specified time delay.
    :param text: The text to print
    :param new_line: Whether the function should add a new line after printing the specified text
    :param delay: The time delay in seconds between printing each character
    :return:
    """
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)

    if new_line:
        print('')


def create_join_game_procedure():
    """
    This function is a procedure that handles the process of creating a new game
    or joining an existing game getting all relevant information from the client
    and handling the process with the server. Once a successful response from the
    server has been received this function will exit so that the game play procedure
    can start.
    :return:
    """

    global game_id

    # Ask if the client would like to create a game or connect to an existing game
    print_slowly("Would you like to [1] create a game [2] connect to a game: ", False)
    start_game = input()

    # Process if the player wishes to crate new game
    if start_game == '1':
        message_response = f"START-GAME~{start_game}"
        networking.send_message(message_response, client_socket, HEADER)

        # Wait for response that new game has been started
        receive_response()

        # Wait for the game ID and set the global game ID
        response_command, response_body = receive_response()
        if response_command == 'SET-ID':
            game_id = response_body
        else:
            print("[ERROR] Invalid response from server, expected game ID")
            print(f"[ERROR INFO] Response received: '{response_command, response_body}'")

    # Process if the player wishes to join an existing game
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
            # If joining a game was unsuccessful restart the procedure
            create_join_game_procedure()

    else:
        # If the player entered an invalid option restart the procedure
        print_slowly("Please enter a valid option.")
        create_join_game_procedure()


def game_play_procedure():
    """
    The actual procedure for playing the game. This function will continuously listen for a
    message from the server while the game is in play and process the message accordingly by
    prompting the user for input if it is required or continuing to the next iteration of the
    loop and letting the receive_response function handle the message if it is purely informational
    :return:
    """

    game_in_play = True

    while game_in_play:

        response_command, response_body = receive_response()

        if response_command == "YOUR-TURN":
            print_slowly(response_body, False)
            message_response = input()
            message_response = f"PLAY-TURN~{game_id}${message_response}"
            networking.send_message(message_response, client_socket, HEADER)

        elif response_command == "END-GAME":
            create_join_game_procedure()

        elif response_command == "CLOSE-GAME":
            pass

        # Continue to the next iteration of the loop and listen for another message if it is an info message
        elif response_command == 'INFO':
            continue



def start_client():
    """
    Method to start the client. Creates and sets all necessary variables and
    handles the intial procedure to get the game set up.
    """

    global SERVER_ADDR, SERVER_PORT, client_socket

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

    # Start the create / join game procedure
    create_join_game_procedure()

    # Start the game play procedure
    game_play_procedure()

if __name__ == '__main__':
    start_client()
