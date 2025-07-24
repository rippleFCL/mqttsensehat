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
        super().__init__(get_offset=CircleRainbowOffset(4.5, 4.5, 5), delay=delay)


class CircleRainbowFast(CircleRainbow):
    def __init__(self, delay: float = 0.01):
        super().__init__(delay=delay)


class SpinningRainbow(Rainbow):
    def __init__(self, delay: float = 0.05):
        super().__init__(get_offset=SpinRainbowOffset(1), delay=delay)


class SpinningRainbowFast(SpinningRainbow):
    def __init__(self, delay: float = 0.01):
        super().__init__(delay=delay)
