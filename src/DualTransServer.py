#DualTransServer.py

import sys
from socket import * 
import thread
from threading import Timer
import time
import random
import logging

class DualTransServer(object):
    """
    A simple server module listening to the port,
    as one client connected to the port, the server send heard beat data to the remote client
    and echo the data the client send to the server.
    It can handle plenty of clients for transmitting in each thread.
    """
    def __init__(self, listenPort = 8080, bufferSize = 2048, needAutoClose = False):
        self.listenPort = listenPort
        self.bufferSize = bufferSize
        self.host = ""
        self.serverAdd = (self.host, self.listenPort)
        self.needAutoClose = needAutoClose
        self.log = logging.getLogger()

    def timerHandler(self, clientsock):
        """
        use for sending heart beat data to client
        """        
        timestr = time.ctime(time.time())
        
        try:
            clientsock.send(timestr.encode('ascii') + " :HeartBeats"  + "\r\n")
            
        except:
            #Don't know how to handle this kind of exception, close socket
            print ("Socket was closed before sending data: %s" % sys.exc_info()[0])
            self.log.info("Socket was closed before sending data: %s" % sys.exc_info()[0])
            clientsock.close()
            #raise
        #problem: cannot find socket.error
        #except socket.error , e:
        #    print ("Error with socket: %s" % e)
        #except socket.herror , e:
        #    print ("Herror with socket: %s" % e)
        #except socket.timeout , e:
        #    print ("Timeout with socket: %s" % e)
        else:
            #if no exception, continue next loop
            t = Timer(1.0, self.timerHandler, [clientsock])
            t.start()
        finally:
            pass
    
    def autoCloseClient(self, clientsock):
        """
        Delay some time and disconnect the client.
        """
        time_period = random.randint(15, 60)
        print ("After %d secs to auto close the client." % (time_period))
        self.log.info("After %d secs to auto close the client." % (time_period))
        time.sleep(time_period)
        print ("Auto close the client.")
        self.log.info("Auto close the client.")
        clientsock.close();
    
    def serverHandler(self, clientsock, addr):
        """
        to handle the accepted connection in a thread
        """
        self.timerHandler(clientsock)
        while True:
            try:
                #if closed in autoCloseClient, here will encounter an exception
                data = clientsock.recv(self.bufferSize)
            except:
                #Don't know how to handle this kind of exception, close socket
                print ("Socket was closed before receive data: %s" % sys.exc_info()[0])
                self.log.info("Socket was closed before receive data: %s" % sys.exc_info()[0])
                break
            else:
                if not data: break
                timestr = time.ctime(time.time())
                print("%s--Recv fr%s, datalen=%d" % (timestr.encode('ascii'), addr, len(data)))
                self.log.info("%s--Recv fr%s, datalen=%d" % (timestr.encode('ascii'), addr, len(data)))
                clientsock.send(timestr.encode('ascii') + " :Get Bytes " + str(len(data)) + "\r\n")
      
        print("client--%s:%d closed." %(addr[0],addr[1]))
        self.log.info("client--%s:%d closed." %(addr[0],addr[1]))
        clientsock.close() 

    def serveForever(self):
        """
        create threads with listening the port
        """
        serversock = socket(AF_INET, SOCK_STREAM)
        serversock.bind(self.serverAdd)
        serversock.listen(7)
    
        while True:
            print("Waiting for connecting with port = %d..." % (self.listenPort))
            self.log.info("Waiting for connecting with port = %d..." % (self.listenPort))
            clientsock, addr = serversock.accept()
    
            print("...connected from-> %s:%d" %(addr[0],addr[1]))
            self.log.info("...connected from-> %s:%d" %(addr[0],addr[1]))
            #Create a new thread to handle this socket
            thread.start_new_thread(self.serverHandler, (clientsock, addr))
            
            #delay to close it self
            if self.needAutoClose:
                thread.start_new_thread(self.autoCloseClient, (clientsock,))
            
if __name__=="__main__":
    
    if (len(sys.argv) < 3):
        print("parameter: [port] [need auto close=(0,1)]")
        INPUT_SOME = raw_input("Press any key to exit.")
        raise exit(0)
    
    logging.basicConfig(
                        filename    = "networkLogging.log",
                        format      = "No.%(thread)d>>%(message)s",
                        level       = logging.INFO
                        )
    
    theServer = DualTransServer(listenPort = int(sys.argv[1]), needAutoClose = int(sys.argv[2]))
    theServer.serveForever()
    
    