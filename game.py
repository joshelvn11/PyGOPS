import random
import string
import networking
import server


class Game:

    def __init__(self, server_instance, initial_client):
        self.server_instance = server_instance
        self.game_id = ""
        # 2D List to hold player lists
        self.players = [initial_client]
        # List to hold player points
        self.player_points = [0, 0]
        # Variable to hold the current player (by index)
        self.current_player = 0
        # Dictionary of player one's cards
        self.player_one_cards = {'A♠': 1, '2♠': 2, '3♠': 3, '4♠': 4, '5♠': 5, '6♠': 6, '7♠': 7, '8♠': 8, '9♠': 9,
                                 '10♠': 10, 'J♠': 11, 'Q♠': 12, 'K♠': 13}
        # Dictionary of player two's cards
        self.player_two_cards = {'A♣': 1, '2♣': 2, '3♣': 3, '4♣': 4, '5♣': 5, '6♣': 6, '7♣': 7, '8♣': 8, '9♣': 9,
                                 '10♣': 10, 'J♣': 11, 'Q♣': 12, 'K♣': 13}
        # Dictionary of game cards
        self.game_cards = {'A♦': 1, '2♦': 2, '3♦': 3, '4♦': 4, '5♦': 5, '6♦': 6, '7♦': 7, '8♦': 8, '9♦': 9, '10♦': 10,
                           'J♦': 11, 'Q♦': 12, 'K♦': 13}
        self.game_cards_list = list(self.game_cards.keys())

        # List to hold the game cards currently in play
        self.play_stack = []

    # Generates a unique game and ID and returns it back to the server
    def generate_id(self):
        characters = string.ascii_letters + string.digits
        self.game_id = ''.join(random.choice(characters) for _ in range(6))
        self.game_id = self.game_id.upper()
        return self.game_id

    # Adds the requested player to the game
    def add_player(self, player):

        # Add player to the game and start the game procedure if there is currently only one player in the game
        if len(self.players) == 1:
            try:
                # Add player to the game instance player list
                self.players.append(player)

                # Let the player know they joined the game successfully
                networking.send_message(f"TRUE~[JOINED GAME] Joined game {self.game_id}",
                                        self.players[1][0], 64)

                # Let the creator know a new player joined the game
                networking.send_message(f"INFO~[NEW PLAYER] {self.players[0][2]} joined the game!",
                                        self.players[0][0], 64)

                print(f"[STARTING GAME] Starting game with ID: {self.game_id}")

                # Start the game
                self.start_game()

            except Exception as e:
                print(f"[ERROR] Error in add_player() in game.py: {e}")

        elif len(self.players) >= 2:
            # Let the player know they could not join the game
            networking.send_message(f"FALSE~[COULD NOT JOIN] There are already two players in {self.game_id}",
                                    player[0], 64)
        elif len(self.players) == 0:
            pass

    def start_game(self):

        print(f"[LOG] Game {self.game_id} is starting")

        # Reset all game variables
        self.player_points = [0, 0]
        self.player_one_cards = {'A♠': 1, '2♠': 2, '3♠': 3, '4♠': 4, '5♠': 5, '6♠': 6, '7♠': 7, '8♠': 8, '9♠': 9,
                                 '10♠': 10, 'J♠': 11, 'Q♠': 12, 'K♠': 13}
        self.player_two_cards = {'A♣': 1, '2♣': 2, '3♣': 3, '4♣': 4, '5♣': 5, '6♣': 6, '7♣': 7, '8♣': 8, '9♣': 9,
                                 '10♣': 10, 'J♣': 11, 'Q♣': 12, 'K♣': 13}
        self.game_cards = {'A♦': 1, '2♦': 2, '3♦': 3, '4♦': 4, '5♦': 5, '6♦': 6, '7♦': 7, '8♦': 8, '9♦': 9, '10♦': 10,
                           'J♦': 11, 'Q♦': 12, 'K♦': 13}
        self.play_stack = []

        # Shuffle game cards list
        random.shuffle(self.game_cards_list)

        try:
            # Let players know the game is starting
            # Send both players the current card in play
            for player in self.players:
                networking.send_message(f"START-GAME~Game is starting...", player[0], 64)
        except Exception as e:
            print(f"[ERROR] Error in start_game() in game.py start game broadcast: {e}")

    def start_round(self):

        # Add the stop card from the game cards list to the play stack and remove it from the list
        self.play_stack = self.game_cards_list[-1]
        self.game_cards_list.pop()

        # Send both players the current card in play
        for player in self.players:
            networking.send_message(f"INFO~Current card: {self.play_stack}", player[0], 64)
















