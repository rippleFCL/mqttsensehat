import random

from mqttsense.animations.animation import Animation, animation_return

from .base import Rainbow
from .offsets import (
    CircleRainbowOffset,
    FillRainbowOffset,
    RollingRainbowOffset,
    SpinRainbowOffset,
)


class RollingRainbow(Rainbow):
    def __init__(self, delay: float = 0.05, width: int = 5):
        super().__init__(get_offset=RollingRainbowOffset(width), delay=delay)


class RollingRainbowFast(RollingRainbow):
    def __init__(self, delay: float = 0.01, width: int = 5):
        super().__init__(delay=delay, width=width)


class FillRainbow(Rainbow):
    def __init__(self, delay: float = 0.05):
        super().__init__(get_offset=FillRainbowOffset(), delay=delay)


class FillRainbowFast(FillRainbow):
    def __init__(self, delay: float = 0.01):
        super().__init__(delay=delay)


class CircleRainbow(Rainbow):
    def __init__(self, delay: float = 0.05):
        super().__init__(get_offset=CircleRainbowOffset(3.5, 3.5, 5), delay=delay)


class CircleRainbowFast(CircleRainbow):
    def __init__(self, delay: float = 0.01):
        super().__init__(delay=delay)


class SpinningRainbow(Rainbow):
    def __init__(self, delay: float = 0.05):
        super().__init__(get_offset=SpinRainbowOffset(0.01), delay=delay)


class SpinningRainbowFast(SpinningRainbow):
    def __init__(self, delay: float = 0.01):
        super().__init__(delay=delay)


class RandomRainbow(Animation):
    def __init__(self):
        self.effects = [RollingRainbow(), SpinningRainbow(), CircleRainbow()]
        self.start = random.randint(0, len(self.effects) - 1)

    def run(self) -> animation_return:
        self.start += 1
        self.start %= len(self.effects)
        return self.effects[self.start].run()


class RandomRainbowFast(Animation):
    def __init__(self):
        self.effects = [
            RollingRainbowFast(),
            SpinningRainbowFast(),
            CircleRainbowFast(),
        ]
        self.start = random.randint(0, len(self.effects) - 1)

    def run(self) -> animation_return:
        self.start += 1
        self.start %= len(self.effects)
        return self.effects[self.start].run()
