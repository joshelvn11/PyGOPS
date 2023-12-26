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

## The Program
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

### The Game Play Procedure