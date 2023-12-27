import random
import string
import networking


class Game:

    def __init__(self, server_instance, initial_player):
        self.server_instance = server_instance
        self.game_id = ""

        # Int to hold the current round being played
        self.current_round = 0

        # List to hold player objects
        self.players = [initial_player]

        # List to hold player points
        self.player_points = [0, 0]

        # List to hold booleans if each player has made a move for the round
        self.played_turn = [False, False]

        # List to hold the player moves for the round
        self.player_moves = [0, 0]

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

    @staticmethod
    def inverse(number):

        if number == 0:
            return 1
        elif number == 1:
            return 0

    @staticmethod
    def list_cards(cards_coll):
        cards_list = ""

        # If the cards collection passed is a dictionary
        if isinstance(cards_coll, dict):
            for card_number, card in cards_coll.items():
                cards_list += f"{card_number}: [{card}], "

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
        self.current_round = 0
        self.player_points = [0, 0]
        self.player_cards = [
            {1: 'A♠', 2: '2♠', 3: '3♠', 4: '4♠', 5: '5♠', 6: '6♠', 7: '7♠', 8: '8♠', 9: '9♠',
             10: '10♠', 11: 'J♠', 12: 'Q♠', 13: 'K♠'},
            {1: 'A♣', 2: '2♣', 3: '3♣', 4: '4♣', 5: '5♣', 6: '6♣', 7: '7♣', 8: '8♣', 9: '9♣',
             10: '10♣', 11: 'J♣', 12: 'Q♣', 13: 'K♣'}
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

        # Increment the round
        self.current_round += 1

        # Send the round number to the players
        for player in self.players:
            networking.send_message(f"INFO~\n\n---------- Round {self.current_round} ----------",
                                    player.get_socket(), 64)

        # Reset the played turn list
        self.played_turn = [False, False]

        # Reset the player moves
        self.player_moves = [0, 0]

        # Add the top card from the game cards list to the play stack and remove it from the list
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
            networking.send_message("YOUR-TURN~Your turn (pick the card number you wish to play): ",
                                    player.get_socket(), 64)

    def play_turn(self, card_played, player_played):

        # Convert the card to an integer
        try:
            card_played = int(card_played)
        except Exception as e:
            print(f"[ERROR] Error in play_turn() in game.py start game broadcast")
            print(f"[ERROR INFO {e}")

        # Check the move is valid
        if card_played > 13 or card_played < 1:
            networking.send_message("YOUR-TURN~Invalid move, please enter a number from 1 to 13...",
                                    player_played.get_socket(), 64)
            return

        # Check which player made the move
        for index, player in enumerate(self.players):
            if player is player_played:

                # Check the player has the card available to play
                if card_played not in self.player_cards[index]:
                    networking.send_message("YOUR-TURN~Invalid move, you dont have that card, try again: ",
                                            player.get_socket(), 64)
                    return

                # Store the move
                self.player_moves[index] = card_played

                # Check if the other player has played their move yet
                if self.player_moves[self.inverse(index)] > 0:

                    for player_instance in self.players:
                        networking.send_message(f"INFO~Both of you have played, let's find out the "
                                                f"scores...", player_instance.get_socket(), 64)

                    # Start the end round procedure
                    self.end_round()

                else:
                    # Let the current player know they are waiting on the other player
                    networking.send_message(f"INFO~Waiting for "
                                            f"{self.players[self.inverse(index)].get_username()} to play...",
                                            player.get_socket(), 64)

    def end_round(self):

        # Determine winner
        winner_name = None

        if self.player_moves[0] > self.player_moves[1]:
            winner_name = self.players[0].get_username()

            for card in self.play_stack:

                # Add the cards in the play stack to the player's points
                self.player_points[0] += self.game_cards[card]

            # Reset the play stack
            self.play_stack = []

        elif self.player_moves[1] > self.player_moves[0]:
            winner_name = self.players[1].get_username()

            for card in self.play_stack:

                # Add the cards in the play stack to the player's points
                self.player_points[1] += self.game_cards[card]

            # Reset the play stack
            self.play_stack = []

        elif self.player_moves[0] == self.player_moves[1]:
            pass

        for player in self.players:
            networking.send_message(f"INFO~{self.players[0].get_username()} "
                                    f"[{self.player_cards[0][self.player_moves[0]]}] : "
                                    f"[{self.player_cards[1][self.player_moves[1]]}] {self.players[1].get_username()} ",
                                    player.get_socket(), 64)

            # Let players know the round winner or if it was a tie
            if self.player_moves[0] == self.player_moves[1]:
                networking.send_message(f"INFO~It's a tie!", player.get_socket(), 64)
            else:
                networking.send_message(f"INFO~{winner_name} wins this round!", player.get_socket(), 64)

        # Remove the cards that were played from the players hands
        self.player_cards[0].pop(self.player_moves[0])
        self.player_cards[1].pop(self.player_moves[1])

        # Check if there are any cards left to play
        if len(self.player_cards[0]) > 0:
            # If there are cards left in the hand play the next round
            self.start_round()
        else:
            # If the hand is finished end the game
            self.end_game()

    def end_game(self):

        for index, player in enumerate(self.players):

            networking.send_message(f"INFO~\n\n---------- End of Game ----------",
                                    player.get_socket(), 64)

            networking.send_message(f"INFO~{self.players[0].get_username()}'s Points: {self.player_points[0]}, "
                                    f"{self.players[1].get_username()}'s Points: {self.player_points[1]}",
                                    player.get_socket(), 64)

            if self.player_points[0] > self.player_points[1]:
                networking.send_message(f"INFO~{self.players[0].get_username} wins the game!",
                                        player.get_socket, 64)
            elif self.player_points[0] < self.player_points[1]:
                networking.send_message(f"INFO~{self.players[1].get_username} wins the game!",
                                        player.get_socket, 64)
            elif self.player_points[0] == self.player_points[1]:
                networking.send_message(f"INFO~It's a tie!",
                                        player.get_socket, 64)
