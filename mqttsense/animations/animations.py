from typing import Any, Generator, Protocol
from .drawables import Drawable, Delay, Fill
import time
import math


class Animation(Protocol):
    def run(self) -> Generator[Fill | Delay, Any, None]: ...


class FillRainbow(Animation):
    def __init__(self, delay: float = 0.01):
        self.delay = delay

    def get_clr_by_angle(self, angle: float) -> int:
        return int(255 * (math.sin(math.radians(angle))))

    def run(self) -> Generator[Fill | Delay, Any, None]:
        for i in range(90):
            red = self.get_clr_by_angle(i)
            green = self.get_clr_by_angle(i + 60)
            blue = self.get_clr_by_angle(i + 120)

            yield Fill((red, green, blue))
            yield Delay(self.delay)

class StopAnimation(Animation):
    def run(self) -> Generator[Fill | Delay, Any, None]:
        yield Delay(0)
