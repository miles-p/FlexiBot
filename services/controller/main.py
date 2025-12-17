import yaml
import os
from nicegui import ui
import paho.mqtt.client as mqtt

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

# Setup MQTT client
mqtt_client = mqtt.Client()

def connect_mqtt():
    if config and 'host' in config:
        host = config['host'].get('address', 'localhost')
        port = config['host'].get('port', 1883)
        try:
            mqtt_client.connect(host, port, 60)
            mqtt_client.loop_start()
            print(f"Connected to MQTT broker at {host}:{port}")
        except Exception as e:
            print(f"MQTT connection error: {e}")

connect_mqtt()

# Publish motor speed
def publish_speed(motor: int, value: float):
    topic = f"motor{motor}/speed"
    mqtt_client.publish(topic, str(int(value)))

# Build the NiceGUI interface
with ui.column().classes('w-full max-w-4xl mx-auto p-4'):
    ui.label('FlexiBot Controller').classes('text-3xl font-bold text-center mb-6')
    
    with ui.row().classes('w-full justify-center gap-8'):
        # Motor 1 Joystick
        with ui.card().classes('p-4'):
            ui.label('Motor 1').classes('text-xl font-semibold text-center mb-2')
            motor1_label = ui.label('Speed: 0').classes('text-center mb-2 font-mono')
            
            joystick1 = ui.joystick(
                color='blue',
                size=150,
                on_move=lambda e: handle_joystick1(e),
                on_end=lambda e: handle_joystick1_end(),
            )
        
        # Motor 2 Joystick
        with ui.card().classes('p-4'):
            ui.label('Motor 2').classes('text-xl font-semibold text-center mb-2')
            motor2_label = ui.label('Speed: 0').classes('text-center mb-2 font-mono')
            
            joystick2 = ui.joystick(
                color='green',
                size=150,
                on_move=lambda e: handle_joystick2(e),
                on_end=lambda e: handle_joystick2_end(),
            )

def handle_joystick1(e):
    # Map Y coordinate (-1 to 1) to speed (-100 to 100)
    speed = int(e.y * 100)
    motor1_label.set_text(f'Speed: {speed}')
    publish_speed(1, speed)

def handle_joystick1_end():
    motor1_label.set_text('Speed: 0')
    publish_speed(1, 0)

def handle_joystick2(e):
    # Map Y coordinate (-1 to 1) to speed (-100 to 100)
    speed = int(e.y * 100)
    motor2_label.set_text(f'Speed: {speed}')
    publish_speed(2, speed)

def handle_joystick2_end():
    motor2_label.set_text('Speed: 0')
    publish_speed(2, 0)

ui.run(host='0.0.0.0', port=8081, title='FlexiBot Controller')
