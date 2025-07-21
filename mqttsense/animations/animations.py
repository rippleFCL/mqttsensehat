from typing import Any, Generator, Protocol
from .drawables import Drawable, Delay, Fill
import math

animation_return = Generator[Drawable | Delay, Any, None]

class Animation(Protocol):
    def run(self, *args) -> animation_return: ...


class FillRainbow(Animation):
    def __init__(self, delay: float = 0.01):
        self.delay = delay

    def get_clr_by_angle(self, angle: float) -> int:
        return int(255 * abs((math.sin(math.radians(angle)))))

    def run(self, *args) -> animation_return:
        index = 0
        while True:
            index += 1
            index %= 180
            red = self.get_clr_by_angle(index)
            green = self.get_clr_by_angle(index + 60)
            blue = self.get_clr_by_angle(index + 120)
            yield Fill((red, green, blue))
            yield Delay(self.delay)

class FillColor(Animation):
    def __init__(self):
        ...
    def run(self, *args) -> animation_return:
        color = args[0]
        yield Fill(color)

class StopAnimation(Animation):
    def run(self, *args) -> animation_return:
        yield Delay(0)
