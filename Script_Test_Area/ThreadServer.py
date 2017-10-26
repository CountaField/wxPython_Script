import os
import socket
import threading
import SocketServer as ss

SERVER_HOST="10.59.37.17"
SERVER_PORT=0
BUF_SIZE=1024

def Client(ip,port,message):
    sock=socket.socket(socket.AF_INET.socket.SOCK_STREAM)
    sock.connect((ip,port))
    try:
        sock.sendall(message)
        response=sock.recv(BUF_SIZE)
        print "Client received: %s" %response
    finally:
        sock.close()

class ThreadedTCPRequestHandler(ss.BaseRequestHandler):
    def handle(self):
        # Send the echo back to the client
        data = self.request.recv(BUF_SIZE)
        current_thread=threading.current_thread()
        response = '%s: %s' % (current_thread.name, data)
        print("Server sending response [current_process_id: data] = [%s] " % response)
        self.request.send(response)
        return


class ThreadedTCPServer(ss.ThreadingMixIn,ss.TCPServer):
    pass




if __name__=="__main__":
    server = ThreadedTCPServer((SERVER_HOST, SERVER_PORT), ThreadedTCPRequestHandler)
    ip,port=server.server_address
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon=True
    server_thread.start()
    print 'Server loop running on thread: %s' %server_thread.name






