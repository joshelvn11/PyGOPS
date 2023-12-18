import random
import string
import server


class Game:

    def __init__(self, server_instance, initial_client):
        self.server_instance = server_instance
        self.game_id = ""
        self.players = {initial_client[0]: initial_client}

    def generate_id(self):
        characters = string.ascii_letters + string.digits
        self.game_id = ''.join(random.choice(characters) for _ in range(6))
        self.game_id = self.game_id.upper()
        return self.game_id


