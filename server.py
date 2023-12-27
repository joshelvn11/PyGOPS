import socket
import threading
import networking
import game
import player


#  FUNCTION DECLARATION ------------------------------------------------------------------------------------------------
def get_clients():
    return Server.clients


class Server:

    # CLASS VARIABLES --------------------------------------------------------------------------------------------------

    _instance = None
    server_started = False

    # Define constants
    SERVER_ADDR = "localhost"
    PORT = 7020
    ADDR = (SERVER_ADDR, PORT)
    HEADER = 64
    FORMAT = "utf-8"

    # Sever variables
    server_socket = None

    # List to store connected client objects
    clients = []

    # List to store client handling thread objects
    client_threads = []

    # Dictionary to store active games
    games = {}

    # OBJECT INITIALIZATION --------------------------------------------------------------------------------------------
    def __init__(self):
        self.server_running = None

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the Server class.
        This is a singleton meaning that if more than one instance is attempted
        to be created it will return the already existing instance. This is to ensure
        that only one instance of the server class ever exists
        """
        if cls._instance is None:
            cls._instance = super(Server, cls).__new__(cls)

            # Additional initialization code can be added here
            print("Server initialized")

            # Create a socket object
            Server.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to a specific address and port
            Server.server_socket.bind(Server.ADDR)

            # Variable to track the application state
            cls.application_running = True

            # Variable to track the server state
            cls.server_running = False

        return cls._instance

    # METHOD DECLARATION -----------------------------------------------------------------------------------------------

    # Function to start the server
    def start_server(self):
        """
        Starts the server by setting the server running variable to True,
        creating the server worker thread and starting it.
        """

        print("Starting server...")

        self.server_running = True
        server_thread = threading.Thread(target=self.server_worker)
        server_thread.start()

    # Function to shut down the server and close all sockets
    def stop_server(self):
        """
        Method to stop the server from running by closing down all open
        client sockets and the server socket.
        """
        print("Stopping server...")

        # Close all client connections
        print("Closing all client sockets...")
        for player_instance in Server.clients:
            try:
                player_instance.get_socket().close()
                print(f"Closed {player_instance.get_username()}")
            except Exception as e:
                print(f"[ERROR] Error closing client socket {player_instance.get_username()} "
                      f"- {player_instance.get_socket()}")
                print(f"[ERROR INFO] {e}")

        self.server_running = False

        print(f"Server socket {Server.server_socket}")

        # Close the server socket
        Server.server_socket.close()

        print('Server stopped...')

    def server_worker(self):
        """
        Main server thread which constantly listens for new connections from clients
        and handles them appropriately by create a new player object for each new client
        and starting a thread to handle the client and all incoming communications from them.
        """

        print("Server started...")

        # Listen for incoming connections
        Server.server_socket.listen()
        print(f"[SERVER STARTED] Listening on {Server.ADDR[0]}:{Server.ADDR[1]}")

        while self.server_running:

            try:
                # Accept a connection
                # Get the client socket object and client address and assign to variables
                client_socket, client_address = Server.server_socket.accept()  # Blocking code
                print(f"[NEW CONNECTION] New connection from {client_address}")

                # Create a client object and add it to the list of client objects
                player_instance = player.Player(client_socket)
                Server.clients.append(player_instance)

                # Set default username
                player_instance.set_username(f"User: {len(Server.clients)}")

                # Create a new thread to handle the client
                client_thread = threading.Thread(target=self.handle_client, args=(player_instance,))

                # Add the thread to the list of client threads
                self.client_threads.append(client_thread)

                # Start the thread
                client_thread.start()

                # Let the client know they connected successfully
                message_response = f"INFO~[SUCCESS] Successfully connected to this server!"
                networking.send_message(message_response, player_instance.get_socket(), Server.HEADER)

                # List the active threads / connections
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")

            except Exception as e:
                print(f"[ERROR] Error in server_worker() in server.py")
                print(f"[ERROR INFO] {e}")

        print("Server listening stopped")

    def handle_client(self, player_instance):
        """
        Method run as thread in parallel to listen for all incoming communication from
        the player instance passed a parameter. Receives all incoming messages by breaking
        it down to its command and body and either dealing with the data correctly or passing
        it to the appropriate function or module.

        :param player_instance: The player object instance to listen to
        :return:
        """

        connected = True

        # Code will listen for data / messages from the client while they are connected
        while connected:

            try:

                # Receive the header containing the message length and decode it using the UTF-8 format
                data_length = player_instance.get_socket().recv(Server.HEADER).decode(Server.FORMAT)

                # Only attempt to handle the message if it has data (i.e. the header is not empty)
                if data_length:

                    # Parse the value to an integer
                    data_length = int(data_length)

                    # Receive the message data from the client using the data length received from the header
                    # Blocking code - will not pass this line until data is received
                    data_message = player_instance.get_socket().recv(data_length).decode(Server.FORMAT)

                    # Split the string into the command and message content
                    message_command = data_message.split('~')[0]
                    message_body = data_message.split('~')[1]

                    # Process the command and message
                    if message_command == "SET-USERNAME":
                        player_instance.set_username(message_body)
                        message_response = (f"INFO~[SUCCESS] Username set to '{player_instance.get_username()}'"
                                            f" successfully")
                        networking.send_message(message_response, player_instance.get_socket(), Server.HEADER)

                    elif message_command == "START-GAME":

                        print("[STARTING GAME]")
                        message_response = f"INFO~[STARTING NEW GAME]"

                        # Create new game instance and generate a new game ID for the instance
                        game_instance = game.Game(self, player_instance)
                        game_instance_id = game_instance.generate_id()
                        print(f"[LOG] New game started with ID [{game_instance_id}] "
                              f"by {player_instance.get_username()}")

                        # Add the game instance to class dictionary with the ID as the key
                        Server.games[game_instance_id] = game_instance

                        # Respond to the client that the game has started
                        message_response = f"INFO~[GAME STARTED] New Game started with ID: {game_instance_id}"
                        networking.send_message(message_response, player_instance.get_socket(), Server.HEADER)

                        # Set the game ID on the client site
                        message_response = f"SET-ID~{game_instance_id}"
                        networking.send_message(message_response, player_instance.get_socket(), Server.HEADER)

                        message_response = f"INFO~Waiting for another player to join"
                        networking.send_message(message_response, player_instance.get_socket(), Server.HEADER)

                    elif message_command == "JOIN-GAME":

                        # Check if the specified game instance exits
                        if message_body in Server.games:
                            # Pass the player over to the game instance to handle
                            Server.games[message_body].add_player(player_instance)
                        else:
                            # Respond to the client that the game does not exist
                            message_response = f"FALSE~[COULD NOT JOIN] Game does does not exist"
                            networking.send_message(message_response, player_instance.get_socket(), Server.HEADER)

                    elif message_command == "PLAY-TURN":

                        # Split the game id and message from the message body
                        message_game_id = message_body.split("$")[0]
                        message_body = message_body.split("$")[1]

                        # Send the play to the specified game instance as well as the player object that played the turn
                        Server.games[message_game_id].play_turn(message_body, player_instance)

                    # If no data received or if the disconnect message is received from the client close the connection
                    if not data_message or data_message == '!DISCONNECT':
                        connected = False

            except ConnectionAbortedError:
                print(f"[INFO] Connection aborted by {player_instance.get_username()}")
                connected = False

            except Exception as e:
                print(f"[ERROR] Error in handle_client() in server.py")
                print(f"[ERROR INFO] {e}")
                connected = False

        # Remove the client from the list and close the connection
        Server.clients.remove(player_instance)
        player_instance.close_socket()


# APPLICATION LOGIC ----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    """
    Main entry point of the script
    """

    # Create an instance of the Server class
    print("Creating server instance")
    server_instance = Server()

    # Start the server
    print("Starting the server")
    server_instance.start_server()

    # Loop to wait for commands from the user
    while True:
        command = input("$: ")

        if command == 'server-start':
            server_instance.start_server()
        elif command == 'server-stop':
            server_instance.stop_server()
        elif command == 'quit':
            break
        elif command == 'active-clients':
            print("List of currently active clients:")
            for client in server_instance.clients:
                print(client)
        elif command == 'active-clients-sockets':
            for client in server_instance.clients:
                print(client.get_socket())
        elif command == 'active-clients-usernames':
            print("List of currently active client usernames:")
            for client in server_instance.clients:
                print(client.get_username())
        elif command == 'active-games':
            print("List of currently active games:")
            for game_id in Server.games:
                print(f"[{game_id}]: {Server.games[game_id]}")
        else:
            print('Please enter a valid command')
