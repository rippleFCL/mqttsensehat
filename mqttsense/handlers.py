from ast import Sub
import time
import json
import logging
from sense_hat import SenseHat
from paho.mqtt.client import MQTTMessage, Client
from .animations import AnimationController, FillColor, FillRainbow, RollingRainbow, FlashAnimation
from .mqtt import Handler, Subscriber

logger = logging.getLogger(__name__)


class StateHandler(Handler):
    def __init__(self):
        self._client: Client | None = None
        self._subscriber: Subscriber | None = None
        self.topic = "state"
        self.availability_topic = "availability"
        self._rgb = {"r": 255, "g": 255, "b": 255}
        self._state = "OFF"
        self._brightness = 255  # Default brightness value
        self._effect = "off"  # Default effect name

    @property
    def rgb(self) -> dict[str, int]:
        return self._rgb

    @rgb.setter
    def rgb(self, value: dict[str, int]):
        old_rgb = self._rgb
        self._rgb = value
        if old_rgb != value:
            self.publish_state()

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, value: str):
        if value not in ["ON", "OFF"]:
            raise ValueError("State must be 'ON' or 'OFF'")
        old_state = self._state
        self._state = value
        if old_state != value:
            self.publish_state()


    @property
    def brightness(self) -> int:
        return self._brightness

    @brightness.setter
    def brightness(self, value: int):
        if not (0 <= value <= 255):
            raise ValueError("Brightness must be between 0 and 255")
        old_brightness = self._brightness
        self._brightness = value
        if old_brightness != value:
            self.publish_state()

    @property
    def effect(self) -> str:
        return self._effect

    @effect.setter
    def effect(self, value: str):
        old_effect = self._effect
        self._effect = value
        if old_effect != value:
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
            "color": self._rgb,  # current RGB color
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
            "Rolling rainbow": RollingRainbow(),
        }
        self._color_effects = {
            "Flash color": FlashAnimation,
        }

    @property
    def effects(self) -> list[str]:
        return list(self._effects.keys())

    def on_message(self, msg: MQTTMessage):
        payload = json.loads(msg.payload.decode())
        state = payload.get("state", self.state.state)
        brightness = payload.get("brightness", self.state.brightness)
        effect_name = payload.get("effect", None)
        color = payload.get("color", None)
        self.state.brightness = brightness
        self.state.state = state

        logger.debug(f"EffectHandler received message: {payload}")
        logger.debug(f"EffectHandler state: {self.state.state}, brightness: {self.state.brightness}, effect: {self.state.effect}, color: {self.state.rgb}")
        self.controller.brightness = brightness/255
        if effect_name:
            self.state.effect = effect_name

            if effect_name in self._effects:
                effect = self._effects[effect_name]
                self.controller.set_animation(effect)
            elif effect_name in self._color_effects:
                effect = self._color_effects[effect_name]
                color_data = (self.state.rgb["r"], self.state.rgb["g"], self.state.rgb["b"])
                self.controller.set_animation(effect(color=color_data))
            else:
                logger.warning(f"Unknown effect: {effect_name}")
        elif color:
            self.state.rgb = color
            self.state.effect = "none"
            self.controller.set_animation(FillColor((color["r"], color["g"], color["b"])))
        elif state == "OFF":
            self.state.state = "OFF"
            logger.debug("Turning off led")
            self.controller.set_animation(FillColor((0, 0, 0)))

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
            "rgb_command_topic": sub.full_topic(self.effect_handler.topic),
            "effect_list": self.effect_handler.effects,
            "availability_topic": sub.full_topic(self.state_handler.availability_topic),
            "payload_available": "online",
            "payload_not_available": "offline",
            "schema": "json",
            "brightness": True,
            "effect": True,
            "supported_color_modes": ["rgb"],
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
