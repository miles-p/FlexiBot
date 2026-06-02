import os
import paho.mqtt.client as mqtt
import yaml


CONFIG_PATH =  os.path.join("app", "mqtt.yaml")

def get_all_topics(config):
    """Extract all topics from the config"""
    topics = []
    for control_name, control_list in config['controls'].items():
        for control in control_list:
            topics.append(control['topic'])
    return topics

def load_config():
    """Load MQTT configuration from yaml file"""
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)
    
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

    #TODO: send to hardware platform!
    print(f"Received message on {topic}: {payload}")

def main():
    config = load_config()
    topics = get_all_topics(config)
    client = mqtt.Client(userdata={'topics': topics})
    
    # Connect to broker
    host = config['host']['address']
    port = config['host']['port']
    
    print(f"Connecting to {host}:{port}...")
    client.connect(host, port, 60)
    
    # Start loop
    client.loop_forever()

if __name__ == "__main__":
    main()