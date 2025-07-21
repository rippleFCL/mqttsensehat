
from mqttsense.mqtt import Dispatch, MQTTClient
from mqttsense.handlers import LedControler, AnimationHandler
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


led_matrix = LedControler()
andimation_handler = AnimationHandler()


dispatch = Dispatch(config.base_topic)
dispatch.register("led/cmd", led_matrix)
dispatch.register("animation/cmd", andimation_handler)


client = MQTTClient(config.username, config.password, dispatch)
client.connect(config.host)
