import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import time
from racer import Racer

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

# Race-track mechanics and thresholds.
LIGHT_THRESHOLD = 10
SENSOR_CHECK_FREQUENCY = .001
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

# RACE CONDITIONS
FINISH_RACE = False

def has_finished_lap(track_number, last_finished_time):
    return mcp.read_adc(track_number) < LIGHT_THRESHOLD and time.time() - last_finished_time > TIME_THRESHOLD

def check_for_race_completion(racers, number_of_laps):
    min_lap = number_of_laps + 1
    for racer in racers:
        min_lap = min(min_lap, len(racer.lap_times))
    if min_lap > number_of_laps:
        FINISH_RACE = True

def prepare_for_race(racers):
    FINISH_RACE = False
    for racer in racers:
        racer.lap_times = []

def run_race(racers, number_of_laps, socket):
    print 'race starting:  %s' % message
    start_time = time.time()
    for racer in racers:
        racer.lap_times.push(start_time)

    while not FINISH_RACE:
        for racer in racers:
            if has_finished_lap(racer.track_number, racer.lap_times[-1]):
                racer.lap_times.push(time.time())
                print vars(racer)
                socket.write_message(vars(racer))
                check_for_race_completion(racers, number_of_laps)
        time.sleep(SENSOR_CHECK_FREQUENCY)
 
class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
      
    def on_message(self, message):
        print message
        if message == 'GO':
            prepare_for_race(racers)
            run_race(racers, 3, self)
        else:
            self.racers = json.loads(message, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            print self.racers       

        # print 'sending back message: %s' % message[::-1]
        # self.write_message(message[::-1])
 
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
