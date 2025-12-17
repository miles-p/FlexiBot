import yaml
import os
from nicegui import ui
import paho.mqtt.client as mqtt
from threading import Thread

def load_config(file_name):
    # It is best practice to use absolute paths inside containers
    base_path = "/app/" 
    file_path = os.path.join(base_path, file_name)
    
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: {file_name} not found in {base_path}")
        return None

# Load configuration
config = load_config("mqtt.yaml")

# Store topic data: {topic: {"name": friendly_name, "group": group_name, "message": last_message}}
topic_data = {}
ui_labels = {}

# Initialize topic_data from config (now with groups)
if config and 'controls' in config:
    for group_name, items in config['controls'].items():
        for item in items:
            topic_data[item['topic']] = {
                "name": item['name'],
                "group": group_name,
                "message": "Waiting for data..."
            }

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        # Subscribe to all topics from config
        for topic in topic_data.keys():
            client.subscribe(topic)
            print(f"Subscribed to: {topic}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    message = msg.payload.decode('utf-8')
    
    if topic in topic_data:
        topic_data[topic]["message"] = message
        # Update UI label if it exists
        if topic in ui_labels:
            ui_labels[topic].set_text(message)

# Setup MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    if config and 'host' in config:
        host = config['host'].get('address', 'localhost')
        port = config['host'].get('port', 1883)
        try:
            mqtt_client.connect(host, port, 60)
            mqtt_client.loop_forever()
        except Exception as e:
            print(f"MQTT connection error: {e}")

# Start MQTT in background thread
mqtt_thread = Thread(target=start_mqtt, daemon=True)
mqtt_thread.start()

# Build the NiceGUI interface
with ui.column().classes('w-full max-w-3xl mx-auto p-4'):
    ui.label('FlexiBot Dashboard').classes('text-3xl font-bold text-center mb-6')
    
    # Group topics by their group name
    if config and 'controls' in config:
        for group_name, items in config['controls'].items():
            with ui.card().classes('w-full mb-4'):
                # Group header
                ui.label(group_name.replace('_', ' ').title()).classes(
                    'text-xl font-semibold mb-3 capitalize'
                )
                
                # Topics within this group
                for item in items:
                    topic = item['topic']
                    with ui.card().classes('w-full mb-2 p-3 bg-gray-50'):
                        with ui.row().classes('w-full items-center justify-between'):
                            with ui.column().classes('gap-0'):
                                ui.label(item['name']).classes('text-lg font-medium')
                                ui.label(topic).classes('text-xs text-gray-500')
                            # Store reference to the message label for updates
                            ui_labels[topic] = ui.label(topic_data[topic]['message']).classes(
                                'text-lg font-mono bg-white px-3 py-1 rounded border'
                            )

ui.run(host='0.0.0.0', port=8080, title='MQTT Dashboard')