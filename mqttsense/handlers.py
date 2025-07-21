import time
import json
from sense_hat import SenseHat
from paho.mqtt.client import MQTTMessage
from .animations import AnimationController, FillColor, StopAnimation, FillRainbow


class AnimationHandler:
    def __init__(self):
        self.controller = AnimationController()
        self.animations = {
            "stop": StopAnimation(),
            "fill_rainbow": FillRainbow(),
            "fill_color": FillColor()
        }

    def __call__(self, msg: MQTTMessage):
        payload = json.loads(msg.payload.decode())
        for animation_name, args in payload.items():
            if animation_name in self.animations:
                animation = self.animations[animation_name]
                self.controller.set_animation(animation, *args)
            else:
                print(f"Unknown animation: {animation_name}")


class LedControler:
    def __init__(self):
        self.sense = SenseHat()

    def __call__(self, msg: MQTTMessage):
        try:
            payload = json.loads(msg.payload.decode())
            if not isinstance(payload, list):
                print("Invalid payload format. Expected a list of pixels.")
                return
            for cmd in payload:
                if not isinstance(cmd, dict):
                    print("Invalid command format. Expected a dictionary")
                    continue
                for func_name, func_args in cmd.items():
                    if func_name == "delay":
                        time.sleep(*func_args)
                    else:
                        func = getattr(self.sense, func_name, None)
                        if callable(func):
                            func(*func_args)
                        else:
                            print(f"Function {func_name} is not callable or does not exist.")
            else:
                print("Invalid payload format. Expected a list")
        except json.JSONDecodeError:
            print("Failed to decode JSON payload.")
        except Exception as e:
            print(f"An error occurred: {e}")
