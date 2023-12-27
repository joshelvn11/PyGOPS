"""
Utility module for sending messages
"""


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
        except Exception as e:
            # If sending fails, remove the client from the list
            print("[ERROR] error in broadcast in networking.py")
            print(f"[ERROR INFO] {e}")
            clients.remove(client)


# Encodes, creates a header and sends the header and message content
# to the specified recipient
def send_message(data_message, socket_recipient, header):
    """
    Function to send messages to the specified recipient socket. The function
    encodes the message, creates a header, send the header and finally sends
    the message body
    :param data_message: The message content
    :param socket_recipient: The socket of the intended recipient
    :param header: The desired length of the header
    :return:
    """

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
