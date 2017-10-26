import socket
import os
import threading
BUF_SIZE=1024

class ForkingClient():
    def __init__(self,ip,port):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((ip,port))
        print('server connected')
    def run(self):
        # Send the data to server
        current_process_id=os.getpid()
        print 'PID %S Sendin g echo message to the server: "%s" ' % (current_process_id,"Hello DB Server!")
        sent_data_length=self.sock.send("Hello DB SERVER!")
        print " Sent: %d characters,so far..." %sent_data_length

        response=self.sock.recv(BUF_SIZE)
        print "PID %s received: %s" % (current_process_id,response[5:])

    def shutdown(self):
        self.sock.close()


if __name__=='__main__':
    client=ForkingClient('10.59.37.17',9900)
    client.run()


