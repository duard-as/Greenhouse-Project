This repository contains the files needed to do temperature and humidity control for a scale greenhouse. The "main.py" file contains the Python code with Micropython extension for programming
the ESP32 microcontroller, which is responsible for taking the temperature and humidity data provided by the DHT11 sensor.

The file "higrometro.ino" contains the programming to control a resistive soil moisture sensor, to be input to an Arduino, from the same code the sensor readings are received.

The code "Servidor (1).py" contains the programming of an API that links to the ESP32 and outputs real-time graphs in an html page of the data being obtained from the microcontroller.
