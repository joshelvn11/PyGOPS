import random
import string
import networking
import server


class Game:

    def __init__(self, server_instance, initial_player):
        self.server_instance = server_instance
        self.game_id = ""

        # List to hold player objects
        self.players = [initial_player]

        # List to hold player points
        self.player_points = [0, 0]

        # Variable to hold the current player (by index)
        self.current_player = 0

        # List to hold dictionaries of player's cards
        self.player_cards = []

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

    def list_cards(self, cards_coll):
        cards_list = ""

        # If the cards collection passed is a dictionary
        if isinstance(cards_coll, dict):
            for index, card in enumerate(cards_coll):
                cards_list += f"{index + 1}: [{card}], "

        # If the cards collection passed in a list
        elif isinstance(cards_coll, list):
            for card in cards_coll:
                cards_list += f"[{card}] "

        else:
            print(f"[ERROR] Invalid type passed to list_cards(), type passes is {type(cards_coll)}")

        return cards_list

    # Adds the requested player to the game
    def add_player(self, player):

        # Add player to the game and start the game procedure if there is currently only one player in the game
        if len(self.players) == 1:
            try:
                # Add player to the game instance player list
                self.players.append(player)

                # Let the player know they joined the game successfully
                networking.send_message(f"TRUE~[JOINED GAME] Joined game {self.game_id}",
                                        player.get_socket(), 64)

                # Set the game ID on the client site
                message_response = f"SET-ID~{self.game_id}"
                networking.send_message(message_response, player.get_socket(), 64)

                # Let the creator know a new player joined the game
                networking.send_message(f"INFO~[NEW PLAYER] {player.get_username()} joined the game!",
                                        self.players[0].get_socket(), 64)

                print(f"[STARTING GAME] Starting game with ID: {self.game_id}")

                # Start the game
                self.start_game()

            except Exception as e:
                print(f"[ERROR] Error in add_player() in game.py: {e}")

        elif len(self.players) >= 2:
            # Let the player know they could not join the game
            networking.send_message(f"FALSE~[COULD NOT JOIN] There are already two players in {self.game_id}",
                                    player.get_username(), 64)
        elif len(self.players) == 0:
            pass

    def start_game(self):

        print(f"[LOG] Game {self.game_id} is starting")

        # Reset all game variables
        self.player_points = [0, 0]
        self.player_cards = [
            {'A♠': 1, '2♠': 2, '3♠': 3, '4♠': 4, '5♠': 5, '6♠': 6, '7♠': 7, '8♠': 8, '9♠': 9,
             '10♠': 10, 'J♠': 11, 'Q♠': 12, 'K♠': 13},
            {'A♣': 1, '2♣': 2, '3♣': 3, '4♣': 4, '5♣': 5, '6♣': 6, '7♣': 7, '8♣': 8, '9♣': 9,
             '10♣': 10, 'J♣': 11, 'Q♣': 12, 'K♣': 13}
        ]
        self.game_cards = {'A♦': 1, '2♦': 2, '3♦': 3, '4♦': 4, '5♦': 5, '6♦': 6, '7♦': 7, '8♦': 8, '9♦': 9, '10♦': 10,
                           'J♦': 11, 'Q♦': 12, 'K♦': 13}
        self.play_stack = []

        # Shuffle game cards list
        random.shuffle(self.game_cards_list)

        try:
            # Let players know the game is starting
            # Send both players the current card in play
            for player in self.players:
                networking.send_message(f"START-GAME~Game is starting...", player.get_socket(), 64)
        except Exception as e:
            print(f"[ERROR] Error in start_game() in game.py start game broadcast")
            print(f"[ERROR INFO {e}")

        self.start_round()

    def start_round(self):

        print(f"[LOG] Round in game {self.game_id} is starting")

        # Add the stop card from the game cards list to the play stack and remove it from the list
        self.play_stack.append(self.game_cards_list[-1])
        self.game_cards_list.pop()

        # Send both players the current card in play and their hand / cards
        for index, player in enumerate(self.players):
            networking.send_message(f"INFO~{self.players[0].get_username()}'s Points: {self.player_points[0]}, "
                                    f"{self.players[1].get_username()}'s Points: {self.player_points[1]}",
                                    player.get_socket(), 64)
            networking.send_message(f"INFO~Current card: {self.list_cards(self.play_stack)}", player.get_socket(), 64)
            networking.send_message(f"INFO~Your cards: {self.list_cards(self.player_cards[index])}",
                                    player.get_socket(), 64)

        # Ask each player to play their turn
        for player in self.players:
            networking.send_message(f"YOUR-TURN~Your turn (pick the card number you wish to play): ",
                                    player.get_socket(), 64)



















