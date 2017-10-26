import SocketServer
import os
import json
import socket


class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):

        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        address=self.client_address[0]
        print "{} wrote:".format(self.client_address[0])
        print self.data
        json_string=json.dumps(self.data.split(' '))
        print json_string
        astring="the pid is: "+str(os.getpid())
        # just send back the same data, but upper-cased
        self.request.sendto(json_string,address)



if __name__ == "__main__":
    hostname = socket.gethostname()
    HOST, PORT = str(socket.gethostbyname(hostname)), 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
