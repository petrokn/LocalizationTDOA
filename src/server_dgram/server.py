import socket
import sys

from matplotlib import pyplot


class Server:
    def __init__(self):
        pass

    def run(self):

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        server_address = ('localhost', 10000)
        print >> sys.stderr, 'starting up on %s port %s' % server_address
        sock.bind(server_address)

        while True:
            print >> sys.stderr, '\nwaiting to receive message'
            data, address = sock.recvfrom(4096)

            print >> sys.stderr, 'received %s bytes from %s' % (len(data), address)
            print >> sys.stderr, data

            if data:
                sent = sock.sendto(data, address)
                print >> sys.stderr, 'sent %s bytes back to %s' % (sent, address)

    def draw_plot(self):
        pyplot.plot(self.true_positions[:, 0], self.true_positions[:, 1], 'bd', label='True position')
        pyplot.plot(self.estimated_positions[:, 0], self.estimated_positions[:, 1], 'r+', label='Estimated position')
        pyplot.legend(loc='upper right', numpoints=1)
        pyplot.xlabel('X coordinate of target')
        pyplot.ylabel('Y coordinate of target')
        pyplot.title('TDOA Hyperbolic Localization')
        pyplot.axis([-50, 50, -50, 50])
        pyplot.show()