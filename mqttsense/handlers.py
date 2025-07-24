import json
import logging

from paho.mqtt.client import Client, MQTTMessage

from .animations import (
    AnimationController,
    CircleRainbow,
    CircleRainbowFast,
    FillColour,
    FillRainbow,
    FillRainbowFast,
    FlashAnimation,
    FlashAnimationFast,
    RollingRainbow,
    RollingRainbowFast,
    SpinningRainbow,
    SpinningRainbowFast,
)
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
        self.client.publish(
            self.subscriber.full_topic(self.topic),
            json.dumps(state_payload),
            retain=True,
        )

    def publish_availability(self, status: str = "online"):
        """Publish availability status (online/offline)"""
        self.client.publish(
            self.subscriber.full_topic(self.availability_topic), status, retain=True
        )
        logger.info(f"Published availability: {status}")

    def on_startup(self, client: Client, subscriber: Subscriber):
        self._client = client
        self._subscriber = subscriber

        # Set Last Will and Testament for availability
        client.will_set(
            topic=subscriber.full_topic(self.availability_topic),
            payload="offline",
            qos=1,
            retain=True,
        )

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
            "Rolling rainbow fast": RollingRainbowFast(),
            "Fill rainbow": FillRainbow(),
            "Fill rainbow fast": FillRainbowFast(),
            "Spinning rainbow": SpinningRainbow(),
            "Spinning rainbow fast": SpinningRainbowFast(),
            "Circle rainbow": CircleRainbow(),
            "Circle rainbow fast": CircleRainbowFast(),
        }
        self._colour_effects = {
            "Flash colour": FlashAnimation,
            "Flash colour fast": FlashAnimationFast,
        }

    @property
    def effects(self) -> list[str]:
        return list(self._effects.keys()) + list(self._colour_effects.keys())

    def on_message(self, msg: MQTTMessage):
        payload = json.loads(msg.payload.decode())
        state = payload.get("state", self.state.state)
        brightness = payload.get("brightness", self.state.brightness)
        effect_name = payload.get("effect", None)
        colour = payload.get("color", None)
        self.state.brightness = brightness
        self.state.state = state

        logger.debug(f"EffectHandler received message: {payload}")
        logger.debug(
            f"EffectHandler state: {self.state.state}, brightness: {self.state.brightness}, effect: {self.state.effect}, colour: {self.state.rgb}"
        )
        self.controller.brightness = brightness / 255
        if colour:
            self.state.rgb = colour
            self.state.effect = "none"
            self.controller.set_animation(
                FillColour((colour["r"], colour["g"], colour["b"]))
            )
        if effect_name:
            self.state.effect = effect_name

            if effect_name in self._effects:
                effect = self._effects[effect_name]
                self.controller.set_animation(effect)
            elif effect_name in self._colour_effects:
                effect = self._colour_effects[effect_name]
                colour_data = (
                    self.state.rgb["r"],
                    self.state.rgb["g"],
                    self.state.rgb["b"],
                )
                self.controller.set_animation(effect(colour=colour_data))
            else:
                logger.warning(f"Unknown effect: {effect_name}")
        if state == "OFF":
            self.state.state = "OFF"
            logger.debug("Turning off led")
            self.controller.brightness = 0

    def on_startup(self, client: Client, subscriber: Subscriber):
        subscriber.subscribe(self.topic)
        self.controller.brightness = 0
        self.controller.set_animation(FillColour((255, 255, 255)))  # Default animation


class HAAutoDiscovery(Handler):
    def __init__(
        self,
        device_name: str,
        effect_handler: EffectHandler,
        state_handler: StateHandler,
    ):
        self.device_name = device_name
        self.effect_handler = effect_handler
        self.state_handler = state_handler

    def to_ha_id(self):
        """Convert a name to a Home Assistant compatible ID."""
        return self.device_name.lower().replace(" ", "_").replace("-", "_")

    def on_message(self, msg: MQTTMessage): ...

    def get_config(self, sub: Subscriber) -> str:
        config = {
            "name": self.device_name,
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
                "ids": [self.to_ha_id()],
                "name": "SenseHat LED Matrix",
                "manufacturer": "Raspberry Pi Foundation",
                "model": "Sense HAT",
            },
            "unique_id": f"{self.to_ha_id()}_led_matrix",
        }
        return json.dumps(config)

    def on_startup(self, client: Client, subscriber: Subscriber):
        logger.info("HAAutoDiscovery initialized")
        client.publish(
            f"homeassistant/light/mqttsense/{self.to_ha_id()}/config",
            self.get_config(subscriber),
            retain=True,
        )


class AnimationHandler(Handler):
    topic = "animation/cmd"

    def __init__(self, controller: AnimationController):
        self.controller = controller
        self.animations = {
            "fill_rainbow": FillRainbow,
            "fill_colour": FillColour,
            "rolling_rainbow": RollingRainbow,
            "flash_colour": FlashAnimation,
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
