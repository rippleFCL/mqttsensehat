from email.mime import base
from paho.mqtt.client import  MQTTMessage
from mqttsense import led
from mqttsense.mqtt import Dispatch, MQTTClient
from mqttsense.led import LedMatrix
import yaml
from pydantic import BaseModel

class Config(BaseModel):
    username: str
    password: str
    host: str
    base_topic: str


with open("config.yml", "r") as f:
    config = Config.model_validate(yaml.safe_load(f))

led_matrix = LedMatrix()


dispatch = Dispatch(config.base_topic)
dispatch.register("led/cmd", led_matrix)


client = MQTTClient(config.username, config.password, dispatch)
client.connect(config.host)
