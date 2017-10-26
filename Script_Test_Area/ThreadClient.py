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

if __name__=='__main__':
    Client()

