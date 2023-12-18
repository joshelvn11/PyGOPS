import socket
import threading
import networking
import game


def get_clients():
    return Server.clients


class Server:
    _instance = None
    server_started = False

    # Define constants
    SERVER_ADDR = 'localhost'
    PORT = 5069
    ADDR = (SERVER_ADDR, PORT)
    HEADER = 64
    FORMAT = 'utf-8'

    # Dictionary to store connected clients
    clients = {}

    # Dictionary to store active games
    games = {}

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

    # ---------- FUNCTION DEFINITIONS -----

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
        for client_socket in self.clients.values():
            client_socket[0].close()

        # Close the server socket
        self.server_socket.close()

        print('Server stopped...')

    # Server worker to be run as independent thread. Listens for connection requests and
    # starts threads to handle clients
    def server_worker(self):

        print('Server started...')

        # Listen for incoming connections
        self.server_socket.listen()
        print(f"[SERVER-STARTED] Listening on {self.server_address[0]}:{self.server_address[1]}")

        while self.server_running:
            # Accept a connection
            # Get the client socket object and client address and assign to variables
            client_socket, client_address = self.server_socket.accept()  # Blocking code
            print(f"[NEW CONNECTION] {client_address}")

            # Add the new client to the dict with a default username
            Server.clients[client_socket] = [client_socket, client_address, f"User: {len(Server.clients)}"]
            print(f"[CLIENT-LIST] {Server.clients}")

            # Create a new thread to handle the client
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

            # List the active threads / connections
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    # Function to handle individual clients and listen for messages from each client
    def handle_client(self, client_socket):

        connected = True

        # Code will listen for data / messages from the client while they are connected
        while connected:
            try:

                # Receive the header containing the message length and decode it using the UTF-8 format
                data_length = client_socket.recv(Server.HEADER).decode(Server.FORMAT)

                # Only attempt to handle the message if it has data (i.e the header is not empty)
                if data_length:

                    # Parse the value to an integer
                    data_length = int(data_length)

                    # Receive the message data from the client using the data length received from the header
                    # Blocking code - will not pass this line until data is received
                    data_message = client_socket.recv(data_length).decode(Server.FORMAT)

                    # Print the message to the terminal
                    print(f"[{client_socket}] {data_message}")

                    # Split the string into the command and message content
                    message_command = data_message.split('~')[0]
                    message_body = data_message.split('~')[1]

                    # Process the command and message
                    if message_command == 'SET-USERNAME':
                        Server.clients[client_socket][2] = message_body
                        message_response = f"[SUCCESS] Username set to {Server.clients[client_socket]} successfully"
                        networking.send_message(message_response, client_socket, Server.HEADER)
                        print(f"[RESPONSE TO CLIENT] {message_response}")
                    elif message_command == 'START-GAME':
                        if message_body == '1':

                            print("[STARTING GAME]")
                            message_response = f"[STARTING NEW GAME]"
                            networking.send_message(message_response, client_socket, Server.HEADER)
                            print(f"[RESPONSE TO CLIENT] {message_response}")

                            # Create new game instance and generate a new game ID for the instance
                            game_instance = game.Game(self)
                            game_id = game_instance.generate_id()
                            print(f"[NEW GAME] New game started with ID [{game_id}]")

                            # Add the game instance to class dictionary with the ID as the key
                            Server.games[game_id] = game_instance

                            # Respond to the client that the game has started
                            message_response = f"[GAME STARTED] New Game started with ID = {game_id}"
                            networking.send_message(message_response, client_socket, Server.HEADER)
                            print(f"[RESPONSE TO CLIENT] {message_response}")

                    # If no data received or if the disconnect message is received from the client close the connection
                    if not data_message or data_message == '!DISCONNECT':
                        connected = False

                    # Broadcast the message to all clients
                    # networking.broadcast(data_message, client_socket, clients, HEADER)

            except Exception as e:
                print(f"Error: {e}")
                break

        # Remove the client from the list and close the connection
        # clients.remove(client_socket)
        client_socket.close()

    # ---------- APPLICATION LOGIC -----

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



