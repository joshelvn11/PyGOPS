class Player:

    def __init__(self, client_socket):
        self.socket = client_socket
        self.username = ""

    def get_socket(self):
        return self.socket

    def close_socket(self):
        self.socket.close()

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

