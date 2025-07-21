import time
import json
import logging
from sense_hat import SenseHat
from paho.mqtt.client import MQTTMessage
from .animations import AnimationController, FillColor, StopAnimation, FillRainbow, RollingRainbow, FlashAnimation

logger = logging.getLogger(__name__)


class AnimationHandler:
    def __init__(self):
        self.controller = AnimationController()
        self.animations = {
            "stop": StopAnimation,
            "fill_rainbow": FillRainbow,
            "fill_color": FillColor,
            "rolling_rainbow": RollingRainbow,
            "flash_color": FlashAnimation
        }

    def __call__(self, msg: MQTTMessage):
        payload = json.loads(msg.payload.decode())
        for animation_name, args in payload.items():
            if animation_name in self.animations:
                animation = self.animations[animation_name]
                self.controller.set_animation(animation(*args))
            else:
                logger.warning(f"Unknown animation: {animation_name}")


class LedControler:
    def __init__(self):
        self.sense = SenseHat()

    def __call__(self, msg: MQTTMessage):
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
