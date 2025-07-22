
from bdb import effective
from mqttsense.mqtt import Dispatch, MQTTClient
from mqttsense.animations import AnimationController
from mqttsense.handlers import LedHandler, AnimationHandler, EffectHandler
import yaml
from pydantic import BaseModel
import logging




class Config(BaseModel):
    username: str
    password: str
    host: str
    base_topic: str
    log_level: str = "INFO"





with open("config.yml", "r") as f:
    config = Config.model_validate(yaml.safe_load(f))

root_logger = logging.getLogger()
root_logger.setLevel(config.log_level.upper())
console_handler = logging.StreamHandler()
console_handler.setLevel(config.log_level.upper())
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

animation_controller = AnimationController()
led_matrix = LedHandler()
andimation_handler = AnimationHandler(animation_controller)
effect_handler = EffectHandler(animation_controller)


dispatch = Dispatch(config.base_topic)
dispatch.register(led_matrix)
dispatch.register(andimation_handler)


client = MQTTClient(config.username, config.password, dispatch)
client.connect(config.host)
