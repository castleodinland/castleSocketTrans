#main2.py

import sys
from socket import * 
import thread
from threading import Timer
import time


def blankMethod(nothing):
    pass

def timerHandler(clientsock):
    timestr = time.ctime(time.time())
    
    try:
        clientsock.send(timestr.encode('ascii') + " :HeartBeats"  + "\r\n")
    except:
        #Don't know how to handle this kind of exception, close socket
        print ("Unexpected error: %s" % sys.exc_info()[0])
        clientsock.close()
        #raise
    #except socket.error , e:
    #    print ("Error with socket: %s" % e)
    #except socket.herror , e:
    #    print ("Herror with socket: %s" % e)
    #except socket.timeout , e:
    #    print ("Timeout with socket: %s" % e)
    else:
        #if no exception, continue next loop
        t = Timer(1.0, timerHandler, [clientsock])
        t.start()
    finally:
        pass


def serverHandler(clientsock,addr):

    timerHandler(clientsock)
    while True:
        data = clientsock.recv(BUFSIZ)
        
        if not data: break
        timestr = time.ctime(time.time())
        print("%s--Recv fr%s, datalen=%d" % (timestr.encode('ascii'), addr, len(data)))
        clientsock.send(timestr.encode('ascii') + " :Get Bytes " + str(len(data)) + "\r\n")
  
    print("client--%s:%d closed." %(addr[0],addr[1]))
    clientsock.close() 



if __name__=="__main__":
    
    if len(sys.argv) < 2:
        print("Parameter error: must be >2")
        raise exit(0)
    
    HOST = ""
    PORT = int(sys.argv[1])
    BUFSIZ = 2048
    ADDR = (HOST, PORT)
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.bind(ADDR)
    serversock.listen(1)

    while 1:
        print("Waiting for connecting with port = %d..." % (PORT))
        clientsock, addr = serversock.accept()

        print("...connected from-> %s:%d" %(addr[0],addr[1]))
        
        #Is start_new_thread a static method?
        thread.start_new_thread(serverHandler, (clientsock, addr))

