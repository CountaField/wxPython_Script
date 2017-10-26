import socket
import sys

import argparse



def echo_client(osusr,hostid,ipadd,close=False):
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host='10.59.37.17'
    port=9900
    server_address=(host,port)

    print "Connecting to %s port %s " % server_address
    sock.connect(server_address)
    if close==False:
        try:
            message = osusr+','+hostid+','+ipadd+',Login'
            sock.sendall(message)
            #look for response
            amount_received=0
            amount_expected=len(message)

        except socket.errno, e:
            print "Socket error: %s" %str(e)
        except Exception, e:
            print "Other exception: %s" %str(e)
        finally:
            print "Closing connection to the server"
            sock.close()
    else:
        try:
            message = osusr + ',' + hostid + ',' + ipadd+',Logout'
            sock.sendall(message)
            # look for response
            amount_received = 0
            amount_expected = len(message)

        except socket.errno, e:
            print "Socket error: %s" % str(e)
        except Exception, e:
            print "Other exception: %s" % str(e)
        finally:
            print "Closing connection to the server"
            sock.close()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Socket Server Example')
    parser.add_argument('--port', action="store", dest="port", type=int, required=True)
    parser.add_argument('--host',action='store',dest='host',type=str,required=True)
    given_args = parser.parse_args()
    print(given_args)
    port = given_args.port
    echo_client()

