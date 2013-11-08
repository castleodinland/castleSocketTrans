import SocketServer
import time
import threading

class MyTCPHandler(SocketServer.BaseRequestHandler):
    
    def __init__(self, request, client_address, server):
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        #self.ttimer = threading.Timer(2,self.tscheduler(self));
    
#    def tscheduler(self):
#        timestr = time.ctime(time.time()) + "\r\n"
#        #self.request.sendall(self.data.upper())
#        self.request.sendall(timestr.encode('ascii'))
#        self.ttimer.start()
        
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        print ("Connected with a client=\"%s\".\r\n" % (self.client_address[0]))

        #self.ttimer.start()
        self.data = self.request.recv(1024).strip()
        while len(self.data)>0:
            print ("%s wrote: %d"%(self.client_address[0],len(self.data)))
            # just send back the same data, but upper-cased
            timestr = time.ctime(time.time()) + "\r\n"
            
            self.request.sendall(timestr.encode('ascii'))
            self.data = self.request.recv(1024).strip()
        #self.ttimer.cancel()
        print ("RequestHandler Close");


if __name__ == "__main__":
    HOST, PORT = "", 21
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()