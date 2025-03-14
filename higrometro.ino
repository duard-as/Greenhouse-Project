const int sensorPin = A1;  // Pin analógico donde se conecta el higrómetro
const int ledPin = 13;     // Pin digital donde se conecta el LED (puedes cambiar este pin si es necesario)
int valorHumedad;          // Variable para almacenar la lectura de humedad

void setup() {
  Serial.begin(9600);      // Inicializa la comunicación serial a 9600 baudios
  pinMode(sensorPin, INPUT); // Configura el pin del sensor como entrada
  pinMode(ledPin, OUTPUT);  // Configura el pin del LED como salida
}

void loop() {
  // Leer el valor analógico del higrómetro
  valorHumedad = analogRead(sensorPin);
  
  // Clasificar el nivel de humedad
  if (valorHumedad < 500) {
    Serial.println("Suelo húmedo");
  } else if (valorHumedad < 800) {
    Serial.println("Suelo medio seco");
  } else {
    Serial.println("Suelo seco");
  }
  
  // Imprimir el valor de humedad en el Monitor Serial
  Serial.print("Humedad del suelo: ");
  Serial.println(valorHumedad);

  // Controlar el LED según la lectura de humedad
  if (valorHumedad > 800) {
    digitalWrite(ledPin, HIGH);  // Enciende el LED si la humedad es mayor a 800
  } else {
    digitalWrite(ledPin, LOW);   // Apaga el LED si la humedad es 800 o menos
  }

  // Espera 2 segundos antes de la próxima lectura
  delay(2000);
}