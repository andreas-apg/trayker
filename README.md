
<p><img align="center" src="imagens/trayker_simple.png?raw=true" /></p>


O Trayker é um protótipo para automatizar a de coleta de bandejas em restaurantes e lanchonetes. Ele veio para dar mais limpeza e conforto, retirando as bandejas abandonadas nas mesa. Assim, os clientes não ficam sem onde sentar devido a mesas sujas e também não precisam ficar procurando as lixeiras ao ir embora. 

O sistema é dividido em cinco partes: mesas e bandejas adaptadas, um robô coletor, uma interface web que demonstra em tempo real o estado do robô e mesa e uma estação base, responsável pelo processamento entre as demais partes. O vídeo abaixo apresenta uma demonstração do sistema.  


<style>.embed-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; } .embed-container iframe, .embed-container object, .embed-container embed { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }</style><div class='embed-container'><iframe src='https://www.youtube.com/embed/D-C6KesHGfw' frameborder='0' allowfullscreen></iframe></div>


## **Mesas**

Tendo um [ESP32 da Espressif](https://www.espressif.com/en/products/hardware/esp32/resources) como microcontrolador principal, o código da mesa foi desenvolvido em MicroPython. Ela é responsável por processar dados coletados de diversos sensores e então determinar se a mesa possui uma bandeja abandonada pronta para coleta. Comunicação sem fio com a base é realizada através do protocolo [MQTT](https://mqtt.org/).

## **Robô Coletor**

Possui um [Arduino Mega 2560](https://store.arduino.cc/usa/mega-2560-r3) como microcontroador. Programado em C++, é responsável por guiar o robô até o destino determinado pela estação base, utilizando de um algoritmo seguidor de linha. A comunicação sem fio com a base é realizada através do protocolo Bluetooth.

## **Interface Web**

Hospedada pela estação base, rodando em um servidor web criado por [Flask](http://flask.pocoo.org/) em Python. Apresenta informações em tempo real da leitura dos sensores das mesas, qual mesa o robô está atendendo e a fila de coleta de mesas que já estão prontas para coleta. Seus códigos integram HTML, CSS e Javascript.

## **Estação Base**

Programada em Python, as funcionalidades integradas de Bluetooth e WiFi de uma [Raspberry Pi 3 Model B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) foram utilizadas para se comunicar com as mesas e o robô.

## **Códigos**
Todos os códigos estão disponibilizados na página do GitHub no branch "final"

## **Projeto Trayker**

**UTFPR- Campus Curitiba**  
**Engenharia da Computação**  
**Oficinas de Integração 3**  
**2019.1**

#### Equipe:

Andreas Gomes  
Douglas Vicente  
Everson de Souza  
Henrique Batochi  
Giovane Negrini

