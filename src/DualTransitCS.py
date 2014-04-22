#DualTransitCS.py

import sys
from socket import * 
import thread
from threading import Timer


class DualTransitCS(object):
    """

    """
    def __init__(self, server_side_lisPort = 2011, client_side_lisPort = 2012,bufferSize = 2048*10):
        self.server_side_lisPort = server_side_lisPort
        self.client_side_lisPort = client_side_lisPort
        self.bufferSize = bufferSize
        self.host = ""
        self.serverSideAdd = (self.host, self.server_side_lisPort)
        self.clientSideAdd = (self.host, self.client_side_lisPort)
        
        self.SockServer = 0
        #self.Sockclient = 0
        
        self.socketArry = [] #save all the client socket
       
    def ServeSideForever(self):#only one connection can be accepted
        """
        create threads with listening the server client port
        """
        serversock = socket(AF_INET, SOCK_STREAM)
        serversock.bind(self.serverSideAdd)
        serversock.listen(7)
        print("[Server:]Waiting for connecting with port = %d...\n" % (self.server_side_lisPort))
        
        while True:
            self.SockServer, addr = serversock.accept()
            print("[Server:]Connected from-> %s:%d" %(addr[0],addr[1]))
            self.SockServer.settimeout(60)#good, won't make socket non-blocking
            
            while True:
                try:
                    #if closed in autoCloseClient, here will encounter an exception
                    data = self.SockServer.recv(self.bufferSize)
                except:
                    #Don't know how to handle this kind of exception, close socket
                    print ("[Server:]Socket was closed before receive data: %s" % sys.exc_info()[0])
                    break
                else:
                    if not data: break
                    #Get real data here
                    print ("[Server:]Get data len=%d" %(len(data)))
                                        
                    try:
                        for ttsoc in self.socketArry:
                            ttsoc.send(data)
                    except:
                        print ("[Server:]Send data error: %s" % sys.exc_info()[0])
                        break
                    
            print ("[Server:]One Loop finished, restart another.")
            self.SockServer.close()
            
    def ClientSideForever(self):#can be one or more connection
        """
        create threads with listening the client client port
        """
        serversock = socket(AF_INET, SOCK_STREAM)
        serversock.bind(self.clientSideAdd)
        serversock.listen(7)
        print("[Client:]Waiting for connecting with port = %d...\n" % (self.client_side_lisPort))
        
        while True:
            Sockclient, addr = serversock.accept()
            print("[Client:]Connected from-> %s:%d" %(addr[0],addr[1]))
            thread.start_new_thread(self.clientHandler, (Sockclient, addr))
            
    def clientHandler(self, clientsock, addr):
        """
        to handle the accepted connection in a thread
        """
        #save socket to list
        self.socketArry.append(clientsock)
        clientsock.settimeout(45)#good, won't make socket non-blocking
        while True:
            try:
                #if closed in autoCloseClient, here will encounter an exception
                data = clientsock.recv(self.bufferSize)
            except:
                #Don't know how to handle this kind of exception, close socket
                print ("[Client:]Socket was closed before receive data: %s" % sys.exc_info()[0])
                break
            else:
                if not data: break
                #Get real data here
                print ("[Client:]Get data len=%d" %(len(data)))
                try:
                    self.SockServer.send(data)
                except:
                    print ("[Client:]Send data error: %s" % sys.exc_info()[0])
                    break
                
        print ("[Client:]One Loop finished, kill this thread.")
        
        #only make broadcast
        if clientsock in self.socketArry:
            self.socketArry.remove(clientsock)
        clientsock.close()
            
    def StartALL(self):
        thread.start_new_thread(self.ServeSideForever, ())
        thread.start_new_thread(self.ClientSideForever, ())
        
if __name__=="__main__":
    
    if (len(sys.argv) < 2):
        print("parameter: [ServerSidePort] [ClientSidePort]")
        INPUT_SOME = raw_input("Press any key to exit.")
        raise exit(0)
        
    theServer = DualTransitCS(server_side_lisPort = int(sys.argv[1]), 
                              client_side_lisPort = int(sys.argv[2]))
    theServer.StartALL()
    #if the main thread ending, the other son-thread will come up an exception while established
    #so, make a while loop, until......the keyboard send a "KeyboardInterrupt" to stop it
    while True:
        pass
    