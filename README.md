# PyGOPS
PyGOPS is an implementation in Python of the card game 'Game of Pure Strategy'. It is a client server, terminal based 
implementation of the game allowing players to play with each other remotely.

## The Game and Rules
The card game is played between two players. A standard deck of 52 cards is split into sets of the suits. One player 
receives a hand consisting of all the Spaded, the other players receives a hand consisting of all the 
Clubs, the set of Diamond cards is shuffled and placed faced down on the table and finally the Hearts cards are discarded
as they are not used for the game.

The game consisting of thirteen rounds where the object is to attain as many points as possible by winning the Diamond 
cards where the points received are equal to the of the face value of the Diamond cards won. The Jack, Queen and King 
are worth 11, 12 and 13 points respectively and the Ace is worth 1 point.

Each round a Diamond cards is drawn from the deck and placed face up. Each player then chooses a card from their hand to 
use to play to win the Diamond card in play, the player with the higher value card being the one that wins the card in 
play. Each player places their card face down on the table and flips their cards over when both players have played to
reveal their card. The player with the higher value card wins the Diamond in play and the value of the Diamond card is 
added to their score.

In the event of a tie, where both players play a card of equal value, their cards are discarded, the Diamond card 
remains on the table and another Diamond card is drawn and in the subsequent round players play for both cards on the
table. If there is another tie this process continues until one players wins all the Diamond cards in play.

## The Program - How It Works
This CLI Python implementation of the game allows players to play this game online remotely with other players. It 
allows players to create and connect to a server and create a game with a unique ID that may then be shared with other
players to connect to.

To run the game the server script firstly has to be run to create a server instance that then can be connected to. When
creating a server the public IP has to be specified in the script to bind to. If running on a machine in a private
network port forwarding will need to be enabled on the router to allows connections to be forwarded to the server 
machine other only connections on the local network will be possible. The desired port to bind to can also be specified.

The server is designed as a singleton class to ensure only one static instance of the server is running at any given 
point.

Once the server has been started it will continuously listen for new connections from clients. When a new client connects 
the server will create a new thread to handle all incoming data / messages from the client. On creating a new thread
to handle the client an object of the client is created with all essential client data that can then be passed around 
the program to flawlessly communicate with client and easily update any client information from one global object.

On the client side when the client script is run it will ask for the desired IP and port of the server wishing to
connect to. Once a connection has been established the client script will ask for a username to use and then send a
message to the server asking it to set the relevant client objects username to the desired username.

### Communication Protocol

All relevant correspondence between client and server is sent as strings over sockets. They are encoded when being sent
and then decoded when being received. All message strings are split into message command and a message body using a 
tilde (~) as the deliminator. The command tells the client or server what to do with the message body.

Message commands can be broken down into active and passive commands where active commands instruct the client or server 
to do something and the passive command being the "INFO" command which is simply printed to the terminal. These threads
are started and then run as an asynchronous background process so interaction with the server can still take place in 
parallel to handle client communications

On the server side threads are created to continually listen to incoming communications from clients and process it
accordingly. However on the client side a function to listen for incoming messages is only called every time a message 
is expected as per the game play procedure. When a message is expected it will block the script from moving further
until the expected messaged has been received (or times out). Once the message has been received the application logic
will continue based the command that was received until another message is expected where it will wait again.

### The Start / Join Game Procedure

Once a username has been set the client will ask the player if they wish to create a game or join a game.

If a player chooses to create a game the "START-GAME" command is sent to the server where the thread for handling that
client will create a new game object instance passing the client object of the client who created the game as a parameter
to start the games list of clients in the game. The handle client thread will then ask the game object to create a new
game ID which is returned to the client handling thread and then sent back to client as an INFO message. The player can
then pass this message ID onto the other player they wish to play with. 

If a player chooses to connecting to an existing game they are prompted to enter the ID of the game they wish to connect 
to. A "JOIN-GAME" command is then sent to the server with the game ID. The server then checks if the specified game 
exists and if it does it pass the client object of the player requesting to join onto the instance of the game with
ID specified. The game instance object then checks if the game is not full, if it isn't full it then adds the new player
to the list of the clients in the game and initiates the game play procedure. If it is full it lets the client know
joining the game was unsuccessful and the client then re-initiates the start / join game procedure.

### The Game Play Procedure

On the server side the game play procedure starts by setting all the game variables (current round, points and cards) to 
their start game defaults. The Diamond cards are then shuffled. and the round procedure is started.

On the client side it starts an indefinite loops controlled by the game-in-play state variable which will continually 
listen for messages from the server one at a time and process them accordingly based on the specified command.

The round procedure starts by sending current round information to each player i.e. the round number, both player's 
current points, each players hand, and the card(s) in play. The game server then sends the "YOUR-TURN" command to both 
clients which then initiates on the client side the process of prompting each player to select a card to play.

Every time a turn is made by the client it is sent as a "PLAY-TURN" command to the server specifying the game ID they
are currently playing. The handling thread for that client on the server processes the message by finding the matching
game instance of that ID and then passed the move onto the game instance where it can be processed as a move in the 
game as the logic for handling "PLAY-TURN" commands and subsequent responses to the client happens inside the game 
object.

Once the first player has made their move it lets them know the game is still waiting on the move from the other player.
Once the other player has made their move the end round procedure is started whereby the winner is determined, all cards
in the play stack are added to their points are both players are informed of the results. The game then checks if there 
are any more cards in the deck left to play, if there are then the start round procedure is restarted or if there are no
more cards left in the deck the end round procedure is started. In the end game procedure the results of the game
are sent to both clients as well as the end game command which prompts the clients to restart the start / join game
procedure.



## Deployment