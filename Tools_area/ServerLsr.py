import socket
import sys
import argparse
import time

host = '10.59.37.17'
data_payload=2048
backlog=100

def echo_server(port):
    print('Creating Socket...')
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('Enabling IP address reuse')
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server_address=(host,port)
    print('Bind IP address %s and port %s on Server' % (host,port))
    sock.bind(server_address)
    print('Defining Max Connections %s' %backlog)
    sock.listen(backlog)
    while True:
        client,address=sock.accept()
        data=client.recv(data_payload)
        login_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        data_check_list=data.split(',')
        if data:
            if data_check_list[0]!='Administrator':
                if data_check_list[-1]=='Login':
                    logfile=open(r'/server_script/connected_client','a')
                    logfile.write(data+','+login_time+'\n')
                    logfile.close()
                    currentfile=open(r'/server_script/connecting_user','a')
                    currentfile.write(data + ' ' + login_time + '\n')
                    currentfile.close()
                elif data_check_list[-1]=='Logout':
                    exist_users=[]
                    currentfile=open(r'/server_script/connecting_user','r')
                    for line in currentfile:
                        if data_check_list[0] not in line and data_check_list[1] not in line:
                            exist_users.append(line)
                    currentfile.close()
                    currentfile=open(r'/server_script/connecting_user','w+')
                    for x in exist_users:
                        currentfile.write(x)
                    currentfile.close()
        client.close()


if __name__=='__main__':
     parser=argparse.ArgumentParser(description='Socket Server Example')
     parser.add_argument('--port',action="store",dest="port",type=int,required=True)
     given_args=parser.parse_args()
     print(given_args)
     port=given_args.port
     echo_server(port)


