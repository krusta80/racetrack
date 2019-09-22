import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import time

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

# Time and light thresholds
LIGHT_THRESHOLD = 10
TIME_THRESHOLD = 3

# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

def finished_lap(track_number, last_finished_time):
    return mcp.read_adc(track_number) < LIGHT_THRESHOLD and time.time() - last_finished_time > TIME_THRESHOLD
 
class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
      
    def on_message(self, message):
        print 'race starting:  %s' % message
        # Start race and send back updates...
        # Main program loop.
        start_time = time.time()
        lapcounts = [0, 0, 0]
        laptimes = [start_time, start_time, start_time]

        while True:
            for i in range(0, 3):
                if finished_lap(i, laptimes[i]):
                    #print "Car " + str(i+1) + " finished lap " + str(lapcounts[i]+1) + " at " + str(laptimes[i] - start_time) + " seconds."
                    self.write_message(str(i) + "," + str(lapcounts[i]) + "," + str(time.time() - laptimes[i]))
                    laptimes[i] = time.time()
                    lapcounts[i] = lapcounts[i] + 1
            time.sleep(0.001)

        print 'sending back message: %s' % message[::-1]
        self.write_message(message[::-1])
 
    def on_close(self):
        print 'connection closed'
 
    def check_origin(self, origin):
        return True
 
application = tornado.web.Application([
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print '*** Websocket Server Started at %s***' % myIP
    tornado.ioloop.IOLoop.instance().start()
