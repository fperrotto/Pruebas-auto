import network
import socket
from time import sleep
import machine
from machine import Pin
from machine import Timer
import utime

#Configuramos la red Wifi
ssid = 'CasaPI'
password = 'a1a1a1b2b2'

#Inicializacion de motores, ultrasonico y buzzer
Motor_A_Adelante = Pin(18, Pin.OUT)
Motor_A_Atras = Pin(19, Pin.OUT)
Motor_B_Adelante = Pin(20, Pin.OUT)
Motor_B_Atras = Pin(21, Pin.OUT)
Trigger = Pin(15, Pin.OUT)
Echo = Pin(14, Pin.IN)
Buzzer = Pin(13, Pin.OUT)

#Inicializacion de timer para callbacks
timer = Timer()
# Variable para activar/desactivar el sensor y la bocina
sensor_activado = False
bocina_activada = False

#Funciones para controlar los motores
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

#Funcion para activar o desactivar la bocina
def bocina():
    global bocina_activada
    bocina_activada = not bocina_activada
    if bocina_activada:
        Buzzer.value(1)
    else:
        Buzzer.value(0)

#Funcion para medir distancia y activar el buzzer dependiendo la distancia
def medir_distancia(timer):
    if sensor_activado:
        Trigger.high()
        utime.sleep(0.00001)
        Trigger.low()
        
        while Echo.value() == 0:
            comienzo = utime.ticks_us()
        while Echo.value() == 1:
            final = utime.ticks_us()

        duracion = final - comienzo #Calcula la duracion del pulso
        distancia = int((duracion * 0.0343) / 2) #Calcula la distancia

        print(distancia)

        #Control del buzzer dependiendo la distancia
        if distancia > 40:
            Buzzer.value(0)
        elif (distancia <= 40) and (distancia > 35):
            Buzzer.value(1)
            utime.sleep(0.3)
            Buzzer.value(0)
            utime.sleep(0.15)
        elif (distancia <= 35) and (distancia > 25):
            Buzzer.value(1)
            utime.sleep(0.15)
            Buzzer.value(0)
            utime.sleep(0.05)
        elif (distancia <= 25) and (distancia > 15):
            Buzzer.value(1)
        elif (distancia <= 15):
            detener() #Detiene el auto debido a que esta muy cerca de un objeto
            Buzzer.value(0)
            
#Funcion para prender o apagar el sensor
def toggle_sensor():
    global sensor_activado
    sensor_activado = not sensor_activado
    if sensor_activado:
        print("Sensor activado.")
    else:
        print("Sensor desactivado.")
        
detener()

#Funcion para conectar la red Wifi
def conectar():
    red = network.WLAN(network.STA_IF)
    red.active(True)
    red.connect(ssid, password)
    while red.isconnected() == False:
        print('Conectando ...')
        sleep(1)
    ip = red.ifconfig()[0] #Obtiene la ip
    print(f'Conectado con IP: {ip}') #Imprime la ip
    return ip
    
def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

#Funcion que genera la pagina web
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

#Funcion que maneja las conexiones y peticiones
def serve(connection):
    while True:
        cliente = connection.accept()[0]
        peticion = cliente.recv(1024) #Recibe peticion
        peticion = str(peticion)
        try:
            peticion = peticion.split()[1] #Obtiene la accion de la peticion
        except IndexError:
            pass
        
        #Llama funciones dependiendo la peticion
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
        if peticion =='/bocina?':
            bocina()
        if peticion == '/sensor?':
            toggle_sensor()
        #Si el sensor esta activado crea un callback de frecuencia 2 que llama a medir_distancia
        if sensor_activado:
            timer.init(freq=5, mode=Timer.PERIODIC, callback=medir_distancia)
        #Si el sensor esta desactivado detiene el timer
        else:
            timer.deinit()
        sleep(1)

        html = pagina_web() #genera la pagina web
        cliente.send(html)
        cliente.close()

try:
    ip = conectar() #Conecta la red Wifi
    connection = open_socket(ip) 
    serve(connection) #Llama a la funcion serve, pasandole la conexion
except KeyboardInterrupt:
    machine.reset() # Reinicia la máquina si se interrumpe el programa

    
