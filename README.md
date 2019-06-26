# **Project Trayker**

Code files for a system that automatically collects trays from empty seats in a restaurant like setting. The project is divided in three main parts: the *Tables*, the *Base* and the *Robot*.

## **Table**

![Schematic of the Table](/imagens/Mesa_parte.png?raw=true)

The tables consist of multiple sensors connected to an [ESP32 microcontroller](https://www.espressif.com/en/products/hardware/esp32/resources). Coded in MicroPython, the data gathered is processed and sent to the Base wirelessly, using [MQTT](https://mqtt.org/).

## **Base**

![Schematic of the Base](/imagens/Base_parte.png?raw=true)

The base consist of a single Raspberry Pi running Debian. Coded in Python3, the data received from the tables is used to create a task queue of which tables have trays to be picked up. This information is then sent to the Robot through [Bluetooth](https://www.bluetooth.com/).

## **Robot**

![Schematic of the Base](/imagens/Robo_parte.png?raw=true)

An Arduino Mega is used to control a three wheeled omni-direcional robot through the restaurant. After receiving a destination from the Base, the robot proceeds to pick up unless the task is cancelled, at which case it returns to its starting position before attending the next item in the task queue.
