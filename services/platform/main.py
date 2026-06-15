import os
import time
import paho.mqtt.client as mqtt
import yaml
import serial


CONFIG_PATH = os.path.join("app", "mqtt.yaml")
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

ser = None


def open_serial():
    while True:
        try:
            s = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"Serial connected on {SERIAL_PORT}")
            return s
        except Exception as e:
            print(f"Serial open failed: {e}, retrying in 5s...")
            time.sleep(5)


def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)


def get_all_topics(config):
    topics = []
    for control_list in config['controls'].values():
        for control in control_list:
            topics.append(control['topic'])
    return topics


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        for topic in userdata['topics']:
            client.subscribe(topic)
            print(f"Subscribed to: {topic}")
    else:
        print(f"Connection failed with code {rc}")


def on_message(client, userdata, msg):
    global ser
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    print(f"MQTT -> Serial [{topic}:{payload}]")
    try:
        ser.write(f"{topic}:{payload}\n".encode('utf-8'))
    except Exception as e:
        print(f"Serial write error: {e}")
        ser = open_serial()


def main():
    global ser
    config = load_config()
    topics = get_all_topics(config)

    ser = open_serial()

    client = mqtt.Client(userdata={'topics': topics})
    client.on_connect = on_connect
    client.on_message = on_message

    host = config['host']['address']
    port = config['host']['port']

    print(f"Connecting to {host}:{port}...")
    client.connect(host, port, 60)
    client.loop_start()

    while True:
        try:
            line = ser.readline().decode('utf-8', errors='replace').strip()
        except Exception as e:
            print(f"Serial read error: {e}")
            ser = open_serial()
            continue

        if not line or ':' not in line:
            continue

        topic, _, value = line.partition(':')
        topic = topic.strip()
        value = value.strip()

        if topic in topics:
            client.publish(topic, value)
            print(f"Serial -> MQTT [{topic}:{value}]")
        else:
            print(f"Serial (unknown topic): {line}")


if __name__ == "__main__":
    main()
