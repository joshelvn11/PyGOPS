import server
import client

start_instructions = input('Would you like to start a server [1] or the client [2]: ')

if start_instructions == '1':
    server.start_server()
elif start_instructions == '2':
    client.start_client()
else:
    print("Please enter a valid option")