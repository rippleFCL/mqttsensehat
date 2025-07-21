from typing import Any, Callable
from paho.mqtt.client import Client, ConnectFlags, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.reasoncodes import ReasonCode
from paho.mqtt.properties import Properties
import logging

logger = logging.getLogger(__name__)


class Dispatch:
    def __init__(self, base_topic: str):
        self.base_topic = base_topic
        self.dispatchers: dict[str, Callable[[MQTTMessage]]] = {}

    def register(self, topic: str, callback: Callable[[MQTTMessage], None]):
        self.dispatchers[self._topic_str(topic)] = callback

    def _topic_str(self, topic: str) -> str:
        return f"{self.base_topic}/{topic}"

    @property
    def topics(self) -> list[str]:
        topics: list[str] = []
        for topic in self.dispatchers.keys():
            topics.append(topic)
        return topics

    def on_message(self, msg: MQTTMessage):
        topic = msg.topic
        if topic in self.dispatchers:
            callback = self.dispatchers[topic]
            callback(msg)
        else:
            logger.warning(f"No dispatcher registered for topic: {topic}")


class MQTTClient:
    def __init__(self, username: str, password: str, dispatch: Dispatch):
        self.client = Client(CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.username = username
        self.password = password
        self.dispatch = dispatch

    def on_connect(
        self, client: Client, userdata: Any, flags: ConnectFlags, reason_code: ReasonCode, properties: Properties | None
    ):
        if reason_code == 0:
            logger.info("Connected successfully")
        else:
            logger.error(f"Connection failed with reason code: {reason_code}")
        for topic in self.dispatch.topics:
            client.subscribe(topic)

    def on_message(self, client: Client, userdata: Any, msg: MQTTMessage):
        try:
            self.dispatch.on_message(msg)
        except Exception as e:
            logger.error(f"Error processing message on topic {msg.topic}: {e}")

    def connect(self, host: str, port: int = 1883, keepalive: int = 60):
        self.client.username_pw_set(self.username, self.password)
        self.client.connect(host, port, keepalive)
        self.client.loop_forever()
