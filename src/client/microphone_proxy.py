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
        # message = 'This is the message.  It will be repeated.'

        try:
            # Send data
            logging.info("Sending data from microphone with id %s.", self.id)

            # print >> sys.stderr, 'sending "%s"' % message
            sent = sock.sendto(self.message, server_address)

            # Receive response
            # print >> sys.stderr, 'waiting to receive'
            logging.info("Data sent. Awaiting for response.")

            data, server = sock.recvfrom(4096)

            logging.info("Received server response.")
            # print >> sys.stderr, 'received "%s"' % data

        finally:
            # print >> sys.stderr, 'closing socket'
            
            logging.info("Closing microphone's socket with id %s.", self.id)

            sock.close()

            logging.info("Closed microphone's socket with id %s.", self.id)
