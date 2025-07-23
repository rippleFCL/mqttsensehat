import logging

import yaml
from pydantic import BaseModel

from mqttsense.animations import AnimationController
from mqttsense.handlers import (
    AnimationHandler,
    EffectHandler,
    HAAutoDiscovery,
    StateHandler,
)
from mqttsense.mqtt import Dispatch, MQTTClient


class Config(BaseModel):
    username: str
    password: str
    host: str
    base_topic: str
    device_name: str
    log_level: str = "INFO"
    ha_discovery: bool = False


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

state_handler = StateHandler()
effect_handler = EffectHandler(animation_controller, state_handler)
animation_handler = AnimationHandler(animation_controller)


dispatch = Dispatch(config.base_topic)
dispatch.register(animation_handler)
dispatch.register(effect_handler)
dispatch.register(state_handler)

if config.ha_discovery:
    ha_auto_discovery = HAAutoDiscovery(
        config.device_name, effect_handler, state_handler
    )
    dispatch.register(ha_auto_discovery)


client = MQTTClient(config.username, config.password, dispatch)
client.connect(config.host)
