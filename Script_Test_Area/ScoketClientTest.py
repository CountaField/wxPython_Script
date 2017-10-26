import socket
import sys
import json
import os
hostname=socket.gethostname()
HOST, PORT = str(socket.gethostbyname(hostname)), 9999
#data = "".join(sys.argv[1:])
data = "what is this"
print data

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendto(data + "\n",HOST)

    # Receive data from the server and shut down
    json_string,addr = sock.recvfrom(1024)
    mylist=json.loads(json_string)
    #print mylist
finally:
    sock.close()

print "Sent:     {}".format(data)
print "Received: ",mylist