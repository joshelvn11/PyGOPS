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
    SERVER_ADDR = 'localhost'
    PORT = 5073
    ADDR = (SERVER_ADDR, PORT)
    HEADER = 64
    FORMAT = 'utf-8'

    # List to store connected client objects
    clients = []

    # Dictionary to store active games
    games = {}

    # OBJECT INITIALIZATION --------------------------------------------------------------------------------------------
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Server, cls).__new__(cls)
            # Additional initialization code can be added here
            print('Server initialized')
            # Create a socket object
            cls.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to a specific address and port
            cls.server_address = (Server.SERVER_ADDR, Server.PORT)
            cls.server_socket.bind(cls.server_address)

            # Variable to track the application state
            cls.application_running = True

            # Variable to track the server state
            cls.server_running = True

        return cls._instance

    # METHOD DECLARATION -----------------------------------------------------------------------------------------------

    # Function to start the server
    def start_server(self):

        print('Starting server...')

        server_running = True
        server_thread = threading.Thread(target=self.server_worker)
        server_thread.start()

    # Function to shut down the server and close all sockets
    def stop_server(self):

        print('Stopping server...')

        server_running = False

        # Close all client connections
        for client in self.clients:
            client.close_socket()

        # Close the server socket
        self.server_socket.close()

        print('Server stopped...')

    # Server worker to be run as independent thread. Listens for connection requests and
    # starts threads to handle clients
    def server_worker(self):

        print('Server started...')

        # Listen for incoming connections
        self.server_socket.listen()
        print(f"[SERVER STARTED] Listening on {self.server_address[0]}:{self.server_address[1]}")

        while self.server_running:
            # Accept a connection
            # Get the client socket object and client address and assign to variables
            client_socket, client_address = self.server_socket.accept()  # Blocking code
            print(f"[NEW CONNECTION] New connection from {client_address}")

            # Create a client object and add it to the list of client objects
            player_instance = player.Player(client_socket)
            # Set default username
            player_instance.set_username(f"User: {len(Server.clients)}")

            # Create a new thread to handle the client
            client_thread = threading.Thread(target=self.handle_client, args=(player_instance,))
            client_thread.start()

            # List the active threads / connections
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    # Function to handle individual clients and listen for messages from each client
    def handle_client(self, player):

        connected = True

        # Code will listen for data / messages from the client while they are connected
        while connected:
            try:

                # Receive the header containing the message length and decode it using the UTF-8 format
                data_length = player.get_socket().recv(Server.HEADER).decode(Server.FORMAT)

                # Only attempt to handle the message if it has data (i.e. the header is not empty)
                if data_length:

                    # Parse the value to an integer
                    data_length = int(data_length)

                    # Receive the message data from the client using the data length received from the header
                    # Blocking code - will not pass this line until data is received
                    data_message = player.get_socket().recv(data_length).decode(Server.FORMAT)

                    # Print the message to the terminal
                    # print(f"[{client_socket}] {data_message}")

                    # Split the string into the command and message content
                    message_command = data_message.split('~')[0]
                    message_body = data_message.split('~')[1]

                    # Process the command and message
                    if message_command == 'SET-USERNAME':
                        player.set_username(message_body)
                        message_response = (f"INFO~[SUCCESS] Username set to '{player.get_username()}'"
                                            f" successfully")
                        networking.send_message(message_response, player.get_socket(), Server.HEADER)
                        # print(f"[RESPONSE TO CLIENT] {message_response}")

                    elif message_command == 'START-GAME':

                        print("[STARTING GAME]")
                        message_response = f"INFO~[STARTING NEW GAME]"
                        networking.send_message(message_response, player.get_socket(), Server.HEADER)
                        # print(f"[RESPONSE TO CLIENT] {message_response}")

                        # Create new game instance and generate a new game ID for the instance
                        game_instance = game.Game(self, player)
                        game_id = game_instance.generate_id()
                        print(f"[LOG] New game started with ID [{game_id}] by {player.get_username()}")

                        # Add the game instance to class dictionary with the ID as the key
                        Server.games[game_id] = game_instance

                        # Respond to the client that the game has started
                        message_response = f"INFO~[GAME STARTED] New Game started with ID: {game_id}"
                        networking.send_message(message_response, player.get_socket(), Server.HEADER)
                        # Set the game ID on the client site
                        message_response = f"SET-ID~{game_id}"
                        networking.send_message(message_response, player.get_socket(), Server.HEADER)

                        message_response = f"INFO~Waiting for another player to join"
                        networking.send_message(message_response, player.get_socket(), Server.HEADER)

                    elif message_command == 'JOIN-GAME':

                        if message_body in Server.games:
                            # Pass the player over to the game instance to handle
                            Server.games[message_body].add_player(player)
                        else:
                            # Respond to the client that the game does not exist
                            message_response = f"FALSE~[COULD NOT JOIN] Game does does not exist"
                            networking.send_message(message_response, player.get_socket(), Server.HEADER)
                            # print(f"[RESPONSE TO CLIENT] {message_response}")

                    # If no data received or if the disconnect message is received from the client close the connection
                    if not data_message or data_message == '!DISCONNECT':
                        connected = False

                    # Broadcast the message to all clients
                    # networking.broadcast(data_message, client_socket, clients, HEADER)

            except Exception as e:
                print(f"[ERROR] Error in handle_client() in server.py")
                print(f"[ERROR INFO] {e}")
                break

        # Remove the client from the list and close the connection
        # self.clients.remove(player)
        player.close_socket()


# APPLICATION LOGIC ----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Create an instance of the Server class
    print('Creating server instance')
    server_instance = Server()

    # Start the server
    print('Starting the server')
    server_instance.start_server()

    while True:
        command = input('$: ')

        if command == 'server-start':
            server_instance.start_server()
        elif command == 'server-stop':
            server_instance.stop_server()
        elif command == 'quit':
            break
        elif command == 'active-clients':
            print("List of currently active clients:")
            for client in server_instance.clients.values():
                print(client)
        elif command == 'active-clients-sockets':
            for client in server_instance.clients.values():
                print(client[0])
        elif command == 'active-clients-addresses':
            for client in server_instance.clients.values():
                print(client[1])
        elif command == 'active-clients-usernames':
            print("List of currently active client usernames:")
            for client in server_instance.clients.values():
                print(client[2])
        elif command == 'active-games':
            print("List of currently active games:")
            for game_id in Server.games:
                print(f"[{game_id}]: {Server.games[game_id]}")
        elif command == 'active-games':
            print("List of currently active game ids:")
            for game_id in Server.games:
                print(f"[{game_id}]")
        else:
            print('Please enter a valid command')



