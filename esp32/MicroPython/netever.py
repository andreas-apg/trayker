import network
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect("Apto 1507", "everson123")