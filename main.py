import network
import socket
from time import sleep
import machine
from machine import Pin
import utime

ssid = 'CasaPI'
password = 'a1a1a1b2b2'

Motor_A_Adelante = Pin(18, Pin.OUT)
Motor_A_Atras = Pin(19, Pin.OUT)
Motor_B_Adelante = Pin(20, Pin.OUT)
Motor_B_Atras = Pin(21, Pin.OUT)
Trigger = Pin(15, Pin.OUT)
Echo = Pin(14, Pin.IN)
Buzzer = Pin(13, Pin.OUT)

Estado = 0
distancia = 0

def adelante():
    Motor_A_Adelante.value(1)
    Motor_B_Adelante.value(1)
    Motor_A_Atras.value(0)
    Motor_B_Atras.value(0)
    
def atras():
    Motor_A_Adelante.value(0)
    Motor_B_Adelante.value(0)
    Motor_A_Atras.value(1)
    Motor_B_Atras.value(1)

def detener():
    Motor_A_Adelante.value(0)
    Motor_B_Adelante.value(0)
    Motor_A_Atras.value(0)
    Motor_B_Atras.value(0)

def izquierda():
    Motor_A_Adelante.value(1)
    Motor_B_Adelante.value(0)
    Motor_A_Atras.value(0)
    Motor_B_Atras.value(1)

def derecha():
    Motor_A_Adelante.value(0)
    Motor_B_Adelante.value(1)
    Motor_A_Atras.value(1)
    Motor_B_Atras.value(0)

def sensor():
    global distancia
    global Estado
    Estado = not Estado
    if Estado == 1:
        if distancia > 15:
            Buzzer.value(0)
        if (distancia <= 15) and (distancia > 10):
            Buzzer.value(1)
            utime.sleep(0.75)
            Buzzer.value(0)
        if (distancia <= 10) and (distancia > 5):
            Buzzer.value(1)
            utime.sleep(0.3)
            Buzzer.value(0)
        if (distancia <= 5):
            Buzzer.value(1)

detener()
    
def conectar():
    red = network.WLAN(network.STA_IF)
    red.active(True)
    red.connect(ssid, password)
    while red.isconnected() == False:
        print('Conectando ...')
        sleep(1)
    ip = red.ifconfig()[0]
    print(f'Conectado con IP: {ip}')
    return ip
    
def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def pagina_web():
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            </head>
            <body>
            <center>
            <table>
            <td><form action="./bocina">
            <input type="submit" value="Bocina" style="background-color: #D5D902; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"  />
            </form></td>
            <td><form action="./adelante">
            <input type="submit" value="Adelante" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"  />
            </form></td>
            <td><form action="./sensor">
            <input type="submit" value="Sensor" style="background-color: #D5D902; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"  />
            </form></td>
            </table>
            <table><tr>
            <td><form action="./izquierda">
            <input type="submit" value="Izquierda" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"/>
            </form></td>
            <td><form action="./detener">
            <input type="submit" value="Detener" style="background-color: #FF0000; border-radius: 50px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px" />
            </form></td>
            <td><form action="./derecha">
            <input type="submit" value="Derecha" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"/>
            </form></td>
            </tr></table>
            <form action="./atras">
            <input type="submit" value="Atras" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"/>
            </form>
            </body>
            </html>
            """
    return str(html)

def serve(connection):
    while True:
        cliente = connection.accept()[0]
        peticion = cliente.recv(1024)
        peticion = str(peticion)
        try:
            peticion = peticion.split()[1]
        except IndexError:
            pass
        global distancia
        Trigger.high()
        utime.sleep(0.00001)
        Trigger.low()

        while Echo.value() == 0:
            comienzo = utime.ticks_us()
        while Echo.value() == 1:
            final = utime.ticks_us()

        duracion = final - comienzo
        distancia = int((duracion * 0.0343) / 2)
        utime.sleep(0.1)
        
        print(distancia)
        if peticion == '/adelante?':
            adelante()
        elif peticion =='/izquierda?':
            izquierda()
        elif peticion =='/detener?':
            detener()
        elif peticion =='/derecha?':
            derecha()
        elif peticion =='/atras?':
            atras()
            
        if peticion =='/sensor?':
            sensor()

        html = pagina_web()
        cliente.send(html)
        cliente.close()

try:
    ip = conectar()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()

    
