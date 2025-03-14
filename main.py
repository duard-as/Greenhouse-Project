import dht
import machine
import time
import network
import urequests
from machine import Pin

motor_relay = Pin(13, Pin.OUT)  #Este se encarga de enceder el motor

# Configuración del sensor DHT11 en el pin GPIO 15
sensor = dht.DHT11(Pin(15, Pin.IN, Pin.PULL_UP))


# Configuración de la conexión Wi-Fi
ssid = 'A54'
password = 'cumbo123'

# Función para conectar al Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
    print('Conectado a WiFi:', wlan.ifconfig())

# Función para enviar los datos a la API
def send_data_to_api(temperature, humidity):
    url = "http://192.168.1.181:5000/api/datos"  #URL de la pagina
    data = {
        'temperature': temperature,
        'humidity': humidity
    }
    try:
        # Enviar los datos a la API usando urequests
        response = urequests.post(url, json=data)  # Enviar los datos en formato JSON
        print('Respuesta de la API:', response.text)  # Imprime la respuesta de la API

        if response.status_code == 200:
            print("Datos enviados exitosamente")
        else:
            print(f"Error al enviar datos: {response.status_code}")
    except Exception as e:
        print(f"Error al conectar a la API: {e}")

# Conectar al Wi-Fi
connect_wifi()

# Bucle principal para obtener los datos del sensor y enviarlos
umbral_humedad = 3000

while True:
    # Esperar un poco antes de la siguiente lectura

    try:
        # Lee los datos de temperatura y humedad del sensor DHT11
        sensor.measure()
        temperature = sensor.temperature()  # Temperatura en grados Celsius
        humidity = sensor.humidity()  # Humedad en porcentaje

        # Muestra los resultados en la consola (opcional)
        print("Temperatura: {} C".format(temperature))
        print("Humedad: {} %".format(humidity))

        # Enviar los datos a la API
        send_data_to_api(temperature, humidity)

        if temperature < 30:
            motor_relay.value(1)  # Enciende el LED (o la salida)
            #print("Temperatura superior a 30°C. LED encendido.")
        else:
            motor_relay.value(0)
            #print("Temperatura por debajo de 30°C. LED apagado.")


        # Espera 2 segundos antes de la siguiente lectura
        time.sleep(1)

    except Exception as e:
        print("Error al leer el sensor DHT11:", e)
        time.sleep(2)
