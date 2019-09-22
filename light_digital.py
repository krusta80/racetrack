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

print('Reading MCP3008 values, press Ctrl-C to quit...')

# Main program loop.
start_time = time.time()
lapcounts = [0, 0, 0]
laptimes = [start_time, start_time, start_time]

while True:
    for i in range(0, 3):
        if finished_lap(i, laptimes[i]):
            laptimes[i] = time.time()
            print "Car " + str(i+1) + " finished lap " + str(lapcounts[i]+1) + " at " + str(laptimes[i] - start_time) + " seconds."
            lapcounts[i] = lapcounts[i] + 1
    time.sleep(0.001)
