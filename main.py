
from mqttsense.mqtt import Dispatch, MQTTClient
from mqttsense.handlers import LedControler, AnimationHandler
import yaml
from pydantic import BaseModel

class Config(BaseModel):
    username: str
    password: str
    host: str
    base_topic: str


with open("config.yml", "r") as f:
    config = Config.model_validate(yaml.safe_load(f))

led_matrix = LedControler()
andimation_handler = AnimationHandler()


dispatch = Dispatch(config.base_topic)
dispatch.register("led/cmd", led_matrix)
dispatch.register("animation/cmd", andimation_handler)


client = MQTTClient(config.username, config.password, dispatch)
client.connect(config.host)
