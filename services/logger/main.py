import paho.mqtt.client as mqtt
import yaml
import os 
from datetime import datetime
from pathlib import Path

# Path to config and logs
CONFIG_PATH = os.path.join("app", "mqtt.yaml")
LOG_PATH = os.path.join("app", "logs.txt")

def load_config():
    """Load MQTT configuration from yaml file"""
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def get_all_topics(config):
    """Extract all topics from the config"""
    topics = []
    for control_name, control_list in config['controls'].items():
        for control in control_list:
            topics.append(control['topic'])
    return topics

def log_message(topic, payload):
    """Log message to file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_entry = f"[{timestamp}] {topic}: {payload}\n"
    
    with open(LOG_PATH, 'a') as f:
        f.write(log_entry)
    
    print(log_entry.strip())

def on_connect(client, userdata, flags, rc):
    """Callback when client connects to broker"""
    if rc == 0:
        print("Connected to MQTT broker")
        topics = userdata['topics']
        for topic in topics:
            client.subscribe(topic)
            print(f"Subscribed to: {topic}")
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    """Callback when message is received"""
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    log_message(topic, payload)

def main():
    # Load configuration
    config = load_config()
    topics = get_all_topics(config)
    
    print(f"Loaded {len(topics)} topics from config")
    
    # Create MQTT client
    client = mqtt.Client(userdata={'topics': topics})
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Connect to broker
    host = config['host']['address']
    port = config['host']['port']
    
    print(f"Connecting to {host}:{port}...")
    client.connect(host, port, 60)
    
    # Start loop
    client.loop_forever()

if __name__ == "__main__":
    main()

