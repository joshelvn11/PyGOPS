import random
import string
import networking
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

    def add_player(self, player):

        # Add player to the game and start the game procedure if there is currently only one player in the game
        if len(self.players) == 1:
            # Add player to the game instances player dictionary using the socket as the key
            self.players[player[0]] = player
            # Let the player know they joined the game successfully
            networking.send_message(f"TRUE~[JOINED GAME] Joined game {self.game_id}", player[0], 64)
        elif len(self.players) >= 2:
            # Let the player know they could not join the game
            networking.send_message(f"FALSE~[COULD NOT JOIN] There are already two players in {self.game_id}",
                                    player[0], 64)
        elif len(self.players) == 0:
            pass
