import logging
import socket
import time
from cPickle import dumps


class MicrophoneProxy:
    def __init__(self, server_address, server_port, id):
        self.__server_address = server_address
        self.__server_port = server_port
        self.id = id

    def run(self, message):
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        server_address = (self.__server_address, self.__server_port)

        try:
            # Send data
            logging.info("Sending data from microphone with id %s.", self.id)
            serialized = dumps(message)
            data_len = len(serialized)

            logging.info(" !!!!  Data length is %s id %s", data_len, str(self.id))
            if data_len > 65535 - 28 - 36:

                data = [serialized[i:i + 65000] for i in range(0, data_len, 65000)]

                for i in range(len(data)):
                    logging.info("Sending %s chunk from mic with id %s and len %s", i, self.id, len(data[i]) + 36)

                    sock.sendto(str(self.id) + data[i], server_address)
                    time.sleep(0.5)
            else:
                sock.sendto(str(self.id) + serialized, server_address)

            time.sleep(0.1)
            sock.sendto(str(self.id), server_address)
            logging.info("Sending info chunk from mic with id %s and len %s", self.id, len(str(self.id)))
            logging.info("Data sent.")
        finally:
            logging.info("Closing microphone's socket with id %s.", self.id)

            sock.close()

            logging.info("Closed microphone's socket with id %s.", self.id)
