import network
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect("Trayker", "Traykson")
