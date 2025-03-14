from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import os
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para evitar errores en servidores
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

app = Flask(__name__)

# Archivo para almacenar los datos
DATA_FILE = 'datos.csv'

# Cargar o inicializar el DataFrame
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])  # Convertir timestamp a formato datetime
else:
    df = pd.DataFrame(columns=['temperature', 'humidity', 'timestamp'])

# Limpiar datos si exceden 100 registros
def clean_data():
    global df
    if len(df) > 100:
        df = df.iloc[25:].reset_index(drop=True)

# Ruta para recibir datos del ESP32
@app.route('/api/datos', methods=['POST'])
def recibir_datos():
    global df
    if request.is_json:
        try:
            data = request.get_json()
            temperature = float(data.get('temperature', 0))  # Convertir a float para evitar errores
            humidity = float(data.get('humidity', 0))
            timestamp = datetime.now()

            # Agregar nuevos datos
            new_data = pd.DataFrame([[temperature, humidity, timestamp]],
                                    columns=['temperature', 'humidity', 'timestamp'])
            df = pd.concat([df, new_data], ignore_index=True)

            # Limpiar si es necesario
            clean_data()

            # Guardar en el archivo
            df.to_csv(DATA_FILE, index=False)

            print(f"Datos recibidos - Temperatura: {temperature}, Humedad: {humidity}, Timestamp: {timestamp}")
            return jsonify({"message": "Datos recibidos y guardados correctamente"}), 200
        except Exception as e:
            return jsonify({"error": f"Error al procesar los datos: {e}"}), 500
    return jsonify({"error": "El cuerpo de la solicitud debe estar en formato JSON"}), 400

# Ruta principal para mostrar gráficos y alarmas
@app.route('/')
def index():
    global df
    if df.empty:
        return "No hay datos disponibles para mostrar gráficos."

    sns.set_theme(style="whitegrid")

    # Últimos valores
    last_temperature = df['temperature'].iloc[-1]
    last_humidity = df['humidity'].iloc[-1]

    # Alarmas
    alarm_temperature_active = last_temperature >= 28
    alarm_humidity_active = last_humidity >= 80

    # Gráfico de temperatura
    img_temp = io.BytesIO()
    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['temperature'], marker='o', color='#FF6347', label='Temperatura', linewidth=2)
    plt.title('Gráfico de Temperatura', fontsize=24)
    plt.xlabel('Hora', fontsize=16)
    plt.ylabel('Temperatura (°C)', fontsize=16)
    plt.legend(fontsize=14)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(img_temp, format='png')
    plt.close()  # Liberar recursos
    img_temp.seek(0)
    temp_chart_url = base64.b64encode(img_temp.getvalue()).decode()

    # Gráfico de humedad
    img_hum = io.BytesIO()
    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['humidity'], marker='o', color='#1E90FF', label='Humedad', linewidth=2)
    plt.title('Gráfico de Humedad', fontsize=24)
    plt.xlabel('Hora', fontsize=16)
    plt.ylabel('Humedad (%)', fontsize=16)
    plt.legend(fontsize=14)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(img_hum, format='png')
    plt.close()  # Liberar recursos
    img_hum.seek(0)
    hum_chart_url = base64.b64encode(img_hum.getvalue()).decode()

    # URLs de iconos y alarmas
    red_light_url = "https://media.istockphoto.com/id/184687428/es/foto/sirena.jpg?s=2048x2048&w=is&k=20&c=t0bhYAVbg6fBGZ4FRP0wpdGd31vEhiNapDHirtaEb74=" 
    temp_icon_url = "https://static.vecteezy.com/system/resources/previews/004/856/822/non_2x/temperature-illustration-on-a-transparent-background-premium-quality-symbols-line-flat-color-icon-for-concept-and-graphic-design-vector.jpg"  # Icono de temperatura
    humidity_icon_url = "https://static.vecteezy.com/system/resources/previews/026/123/610/non_2x/humidity-icon-in-flat-style-climate-illustration-on-white-isolated-background-temperature-forecast-business-concept-vector.jpg"  # Icono de humedad

    # Plantilla HTML
    html_template = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Monitoreo Invernadero</title>
        <style>
            body {
                background-color: #f0f8ff;
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 20px;
            }
            h1 {
                font-size: 60px;
                color: #ff6347;
                font-family: 'Lucida Handwriting', cursive;
                margin-bottom: 20px;
                animation: moveTitle 10s infinite linear;
                text-shadow: 3px 3px 10px rgba(0, 0, 0, 0.3);
                letter-spacing: 4px;
            }
            @keyframes moveTitle {
                0% { transform: translateX(0); }
                50% { transform: translateX(30px); }
                100% { transform: translateX(0); }
            }
            h2 {
                font-size: 30px;
                color: #4682b4;
            }
            img {
                margin: 20px 0;
                border-radius: 10px;
            }
            .chart-container {
                background: #ffffff;
                border-radius: 15px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                padding: 20px;
                margin: 20px 0;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 15px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                padding: 30px;
                margin-top: 50px;
            }
            .alarms {
                display: flex;
                justify-content: space-between;
                margin-bottom: 20px;
                align-items: center;
            }
            .alarm {
                font-size: 24px;
                font-weight: bold;
                color: #d9534f;
                background-color: #f2dede;
                border: 1px solid #d9534f;
                border-radius: 5px;
                padding: 10px;
                width: 45%;
                text-align: center;
            }
            .alarm img {
                width: 50px;
                height: 50px;
                vertical-align: middle;
                margin-right: 10px;
            }
            .alarm-text {
                display: inline-block;
                vertical-align: middle;
                font-size: 20px;
                font-weight: bold;
            }
            .current-status {
                background: #ffffff;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin: 20px 0;
                font-size: 24px;
                font-weight: bold;
                text-align: left;
                animation: slideIn 1s ease-out;
            }
            .current-status img {
                width: 40px;
                height: 40px;
                vertical-align: middle;
                margin-right: 20px;
            }
            @keyframes slideIn {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(0); }
            }
        </style>
    </head>
    <body>
        <h1>Interfaz Web del Invernadero</h1>

        <!-- Estado Actual -->
        <div class="current-status">
            <p><strong>Estado Actual:</strong></p>
            <p><img src="{{ temp_icon_url }}" alt="Temperatura Icon">Temperatura: {{ last_temperature }}°C</p>
            <p><img src="{{ humidity_icon_url }}" alt="Humedad Icon">Humedad: {{ last_humidity }}%</p>
        </div>

        <!-- Alarmas -->
        <div class="alarms">
            {% if alarm_humidity_active %}
            <div class="alarm">
                <img src="{{ red_light_url }}" alt="Alarma Humedad">
                <span class="alarm-text">¡ALERTA! Humedad Alta</span>
            </div>
            {% endif %}
            {% if alarm_temperature_active %}
            <div class="alarm">
                <img src="{{ red_light_url }}" alt="Alarma Temperatura">
                <span class="alarm-text">¡ALERTA! Temperatura Alta</span>
            </div>
            {% endif %}
        </div>

        <!-- Gráficos -->
        <div class="chart-container">
            <h2>Gráfico de Temperatura</h2>
            <img src="data:image/png;base64,{{ temp_chart_url }}" alt="Gráfico de Temperatura">
        </div>

        <div class="chart-container">
            <h2>Gráfico de Humedad</h2>
            <img src="data:image/png;base64,{{ hum_chart_url }}" alt="Gráfico de Humedad">
        </div>

        <script>
            setInterval(function() {
                window.location.reload();
            }, 10000); // Recarga cada 10 segundos
        </script>
    </body>
    </html>
    '''

    return render_template_string(html_template, 
                                  last_temperature=last_temperature,
                                  last_humidity=last_humidity,
                                  alarm_temperature_active=alarm_temperature_active,
                                  alarm_humidity_active=alarm_humidity_active,
                                  temp_chart_url=temp_chart_url,
                                  hum_chart_url=hum_chart_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
