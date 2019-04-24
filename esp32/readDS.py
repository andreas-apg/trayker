import mfrc522BM
from os import uname
import time
from machine import Pin, SPI

sck = Pin(18, Pin.OUT)
mosi = Pin(23, Pin.OUT)
miso = Pin(19)

spi = SPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosio, miso=miso)
spi.init()

def do_read():
        rdr = mfrc522BM.MFRC522(spi, 22, 5)
	rdr2 =  mfrc522BM.MFRC522(spi, 32, 21)
        print("")
        print("Place card before reader to read from address 0x08")
        print("")

        try:
                while True:
			time.sleep(0.5)
			(stat, tag_type) = rdr.request(rdr.REQIDL)
                        if stat == rdr.OK:

                                (stat, raw_uid) = rdr.anticoll()

                                if stat == rdr.OK:
                                        print("New card detected: Board 1")
                                        print("  - tag type: 0x%02x" % tag_type)
                                        print("  - uid   : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                                        print("")

                                        if rdr.select_tag(raw_uid) == rdr.OK:

                                                key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                                                if rdr.auth(rdr.AUTHENT1A, 8, key, raw_uid) == rdr.OK:
                                                        print("Address 8 data: %s" % rdr.read(8))
                                                        rdr.stop_crypto1()
                                                else:
                                                        print("Authentication error")
                                        else:
                                                print("Failed to select tag")
			time.sleep(0.5)
			(stat, tag_type) = rdr.request(rdr.REQIDL)

                        if stat == rdr.OK:
                                (stat, raw_uid) = rdr.anticoll()

                                if stat == rdr.OK:
                                        print("New card detected: Board 2")
                                        print("  - tag type: 0x%02x" % tag_type)
                                        print("  - uid   : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                                        print("")

                                        if rdr.select_tag(raw_uid) == rdr.OK:

                                                key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                                                if rdr.auth(rdr.AUTHENT1A, 8, key, raw_uid) == rdr.OK:
                                                        print("Address 8 data: %s" % rdr.read(8))
                                                        rdr.stop_crypto1()
                                                else:
                                                        print("Authentication error")
                                        else:
                                                print("Failed to select tag")
        except KeyboardInterrupt:
                print("Bye")

