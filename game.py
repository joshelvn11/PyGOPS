import random
import string
import server


class Game:

    def __init__(self, server_instance):
        self.server_instance = server_instance

    def generate_id(self):
        characters = string.ascii_letters + string.digits
        game_id = ''.join(random.choice(characters) for _ in range(6))
        game_id = game_id.upper()
        return game_id


