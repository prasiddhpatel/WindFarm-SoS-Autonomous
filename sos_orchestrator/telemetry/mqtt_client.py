import json
import time
from collections import deque
import paho.mqtt.client as mqtt
from config import settings


class StoreAndForwardClient:
    def __init__(self, max_queue: int = 10000):
        self.queue = deque(maxlen=max_queue)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.connected = False

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        self.connected = True

    def on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        self.connected = False

    def connect(self):
        self.client.connect(settings.mqtt_host, settings.mqtt_port, 60)
        self.client.loop_start()

    def publish_json(self, topic: str, payload: dict, qos: int = 1):
        msg = json.dumps(payload)
        if self.connected:
            self.client.publish(topic, msg, qos=qos)
        else:
            self.queue.append((topic, msg, qos))

    def flush(self):
        while self.connected and self.queue:
            topic, msg, qos = self.queue.popleft()
            self.client.publish(topic, msg, qos=qos)


telemetry_client = StoreAndForwardClient()
