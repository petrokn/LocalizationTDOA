import logging
import socket


class MicrophoneProxy:
    def __init__(self, server_address, server_port, message, id):
        self.__server_address = server_address
        self.__server_port = server_port
        self.message = message
        self.id = id

    def run(self, message):
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        server_address = (self.__server_address, self.__server_port)

        try:
            # Send data
            logging.info("Sending data from microphone with id %s.", self.id)

            sent = sock.sendto(self.message, server_address)

            # Receive response
            logging.info("Data sent. Awaiting for response.")

            data, server = sock.recvfrom(4096)

            logging.info("Received server response.")
        finally:
            logging.info("Closing microphone's socket with id %s.", self.id)

            sock.close()

            logging.info("Closed microphone's socket with id %s.", self.id)
