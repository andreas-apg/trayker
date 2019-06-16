import network
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect("Copel-bel-84", "97198400")
