from ast import Sub
import time
import json
import logging
from sense_hat import SenseHat
from paho.mqtt.client import MQTTMessage, Client
from .animations import AnimationController, FillColor, StopAnimation, FillRainbow, RollingRainbow, FlashAnimation
from .mqtt import Handler, Subscriber

logger = logging.getLogger(__name__)


class StateHandler(Handler):
    def __init__(self):
        self._client: Client | None = None
        self._subscriber: Subscriber | None = None
        self.topic = "state"
        self.availability_topic = "availability"
        self._state = "OFF"
        self._brightness = 255  # Default brightness value
        self._effect = "off"  # Default effect name

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, value: str):
        if value not in ["ON", "OFF"]:
            raise ValueError("State must be 'ON' or 'OFF'")
        self._state = value
        self.publish_state()

    @property
    def brightness(self) -> int:
        return self._brightness

    @brightness.setter
    def brightness(self, value: int):
        if not (0 <= value <= 255):
            raise ValueError("Brightness must be between 0 and 255")
        self._brightness = value
        self.publish_state()

    @property
    def effect(self) -> str:
        return self._effect

    @effect.setter
    def effect(self, value: str):
        self._effect = value
        self.publish_state()

    @property
    def client(self) -> Client:
        if self._client is None:
            raise ValueError("Client is not set")
        return self._client

    @property
    def subscriber(self) -> Subscriber:
        if self._subscriber is None:
            raise ValueError("Subscriber is not set")
        return self._subscriber

    def on_message(self, msg: MQTTMessage): ...

    def publish_state(self):
        # Handle incoming state requests and publish current state
        state_payload = {
            "state": self.state,  # or "OFF" based on your logic
            "brightness": self.brightness,  # current brightness value
            "effect": self.effect,  # current effect name
        }
        self.client.publish(self.subscriber.full_topic(self.topic), json.dumps(state_payload))

    def publish_availability(self, status: str = "online"):
        """Publish availability status (online/offline)"""
        self.client.publish(self.subscriber.full_topic(self.availability_topic), status, retain=True)
        logger.info(f"Published availability: {status}")

    def on_startup(self, client: Client, subscriber: Subscriber):
        self._client = client
        self._subscriber = subscriber

        # Set Last Will and Testament for availability
        client.will_set(topic=subscriber.full_topic(self.availability_topic), payload="offline", qos=1, retain=True)

        # Publish that we're online
        self.publish_availability("online")
        self.publish_state()

        logger.info("StateHandler initialized with client and LWT configured")


class EffectHandler(Handler):
    def __init__(self, controller: AnimationController, state: StateHandler):
        self.controller = controller
        self.state = state
        self.topic = "effect"
        self._effects = {
            "stop": StopAnimation(),
            "fill_rainbow": FillRainbow(),
            "rolling_rainbow": RollingRainbow(),
            "flash_color": FlashAnimation(),
        }

    @property
    def effects(self) -> list[str]:
        return list(self._effects.keys())

    def on_message(self, msg: MQTTMessage):
        payload = json.loads(msg.payload.decode())
        state = payload.get("state", "OFF")
        brightness = payload.get("brightness", 255)
        effect_name = payload.get("effect", None)
        if effect_name:
            if effect_name in self.effects:
                effect = self.effects[effect_name]
                self.controller.set_animation(effect)
            else:
                logger.warning(f"Unknown effect: {effect_name}")
        elif state == "ON":
            self.state.state = "ON"
            self.state.brightness = brightness
            self.controller.set_animation(FillColor((255, 255, 255), brightness))
        else:
            self.state.state = "OFF"
            self.controller.set_animation(StopAnimation())

    def on_startup(self, client: Client, subscriber: Subscriber):
        subscriber.subscribe(self.topic)


class HAAutoDescovery(Handler):
    def __init__(self, effect_handler: EffectHandler, state_handler: StateHandler):
        self.effect_handler = effect_handler
        self.state_handler = state_handler

    def on_message(self, msg: MQTTMessage): ...

    def get_config(self, sub: Subscriber) -> str:
        config = {
            "name": "SenseHat LED Matrix",
            "command_topic": sub.full_topic(self.effect_handler.topic),
            "state_topic": sub.full_topic(self.state_handler.topic),
            "brightness_command_topic": sub.full_topic(self.effect_handler.topic),
            "effect_command_topic": sub.full_topic(self.effect_handler.topic),
            "effect_list": self.effect_handler.effects,
            "availability_topic": sub.full_topic(self.state_handler.availability_topic),
            "payload_available": "online",
            "payload_not_available": "offline",
            "schema": "json",
            "brightness": True,
            "effect": True,
            "dev": {
                "ids": ["mqttsense"],
                "name": "MQTT SenseHat",
                "manufacturer": "Raspberry Pi Foundation",
                "model": "Sense HAT",
            },
            "unique_id": "sensehat01",
        }
        return json.dumps(config)

    def on_startup(self, client: Client, subscriber: Subscriber):
        logger.info("HAAutoDescovery initialized")
        client.publish("homeassistant/light/mqttsense/sensehat01/config", self.get_config(subscriber))


class AnimationHandler(Handler):
    topic = "animation/cmd"

    def __init__(self, controller: AnimationController):
        self.controller = controller
        self.animations = {
            "stop": StopAnimation,
            "fill_rainbow": FillRainbow,
            "fill_color": FillColor,
            "rolling_rainbow": RollingRainbow,
            "flash_color": FlashAnimation,
        }

    def on_message(self, msg: MQTTMessage):
        payload = json.loads(msg.payload.decode())
        for animation_name, args in payload.items():
            if animation_name in self.animations:
                animation = self.animations[animation_name]
                self.controller.set_animation(animation(*args))
            else:
                logger.warning(f"Unknown animation: {animation_name}")

    def on_startup(self, client: Client, subscriber: Subscriber):
        subscriber.subscribe("animation/cmd")


class LedHandler(Handler):
    topic = "led/cmd"

    def __init__(self):
        self.sense = SenseHat()

    def on_message(self, msg: MQTTMessage):
        try:
            payload = json.loads(msg.payload.decode())
            if not isinstance(payload, list):
                logger.error("Invalid payload format. Expected a list of pixels.")
                return
            for cmd in payload:
                if not isinstance(cmd, dict):
                    logger.error("Invalid command format. Expected a dictionary")
                    continue
                for func_name, func_args in cmd.items():
                    if func_name == "delay":
                        time.sleep(*func_args)
                    else:
                        func = getattr(self.sense, func_name, None)
                        if callable(func):
                            func(*func_args)
                        else:
                            logger.error(f"Function {func_name} is not callable or does not exist.")
            else:
                logger.error("Invalid payload format. Expected a list")
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON payload.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    def on_startup(self, client: Client, subscriber: Subscriber):
        subscriber.subscribe("led/cmd")
