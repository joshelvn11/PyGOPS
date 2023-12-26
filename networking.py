def broadcast(data_message, sender_socket, clients, header):

    # Encode the message data
    data_message = data_message.encode()

    # Determine the message data length to create the message header
    data_length = len(data_message)

    # Encode the data length to send
    data_length = str(data_length).encode()

    # Pad the data length to make it 64 bytes
    data_length += b' ' * (header - len(data_length))

    for client in clients:
        try:
            # Send the data length (header) to the client
            client.send(data_length)

            # Send the message data to the client
            client.send(data_message)
        except:
            # If sending fails, remove the client from the list
            clients.remove(client)


# Encodes, creates a header and sends the header and message content
# to the specified recipient
def send_message(data_message, socket_recipient, header):
    # Encode the message data
    data_message = data_message.encode()

    # Determine the message data length to create the message header
    data_length = len(data_message)

    # Encode the data length to send
    data_length = str(data_length).encode()

    # Pad the data length to make it 64 bytes
    data_length += b' ' * (header - len(data_length))

    # Send the data length (header) to the client
    socket_recipient.send(data_length)

    # Send the message data to the client
    socket_recipient.send(data_message)
