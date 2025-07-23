import logging
from typing import Any, Protocol

from paho.mqtt.client import Client, ConnectFlags, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

logger = logging.getLogger(__name__)


class Handler(Protocol):
    def on_message(self, msg: MQTTMessage): ...

    def on_startup(self, client: Client, subscriber: "Subscriber"): ...


class Dispatch:
    def __init__(self, base_topic: str):
        self.base_topic = base_topic
        self.dispatchers: list[Handler] = []
        self.topic_dispatcher: dict[str, Handler] = {}

    def subscribe(self, topic: str, handler: Handler):
        self.topic_dispatcher[topic] = handler

    def register(self, handler: Handler):
        self.dispatchers.append(handler)

    def on_message(self, msg: MQTTMessage):
        topic = msg.topic
        if topic in self.topic_dispatcher:
            handler = self.topic_dispatcher[topic]
            handler.on_message(msg)
        else:
            logger.warning(f"No dispatcher registered for topic: {topic}")

    def on_connect(self, client: Client):
        for dispatcher in self.dispatchers:
            subscriber = Subscriber(client, self, dispatcher, self.base_topic)
            logger.info(f"Starting handler: {dispatcher.__class__.__name__}")
            dispatcher.on_startup(client, subscriber)


class Subscriber:
    def __init__(
        self, client: Client, dispatch: Dispatch, handler: Handler, base_topic: str
    ):
        self.client = client
        self.dispatch = dispatch
        self.handler = handler
        self.base_topic = base_topic

    def full_topic(self, topic: str) -> str:
        return f"{self.base_topic}/{topic}"

    def subscribe(self, topic: str):
        full_topic = self.full_topic(topic)
        self.client.subscribe(full_topic)
        self.dispatch.subscribe(full_topic, self.handler)
        logger.info(
            f"Handler {self.handler.__class__.__name__} Subscribed to topic: {full_topic}"
        )

    def subscribe_full(self, full_topic: str):
        self.client.subscribe(full_topic)
        self.dispatch.subscribe(full_topic, self.handler)
        logger.info(
            f"Handler {self.handler.__class__.__name__} Subscribed to full topic: {full_topic}"
        )


class MQTTClient:
    def __init__(self, username: str, password: str, dispatch: Dispatch):
        self.client = Client(CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.username = username
        self.password = password
        self.dispatch = dispatch

    def on_connect(
        self,
        client: Client,
        userdata: Any,
        flags: ConnectFlags,
        reason_code: ReasonCode,
        properties: Properties | None,
    ):
        if reason_code == 0:
            logger.info("Connected successfully")
            self.dispatch.on_connect(client)
        else:
            logger.error(f"Connection failed with reason code: {reason_code}")

    def on_message(self, client: Client, userdata: Any, msg: MQTTMessage):
        try:
            self.dispatch.on_message(msg)
        except Exception as e:
            logger.exception(f"Error processing message on topic {msg.topic}: {e}")

    def connect(self, host: str, port: int = 1883, keepalive: int = 60):
        self.client.username_pw_set(self.username, self.password)
        self.client.connect(host, port, keepalive)
        self.client.loop_forever()
