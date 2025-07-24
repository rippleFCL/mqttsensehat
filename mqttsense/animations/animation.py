import logging
from typing import Any, Generator, Protocol

from .drawables import Delay, Drawable, Fill
from .utils import scale_brightness

logger = logging.getLogger(__name__)

animation_return = Generator[Drawable | Delay, Any, None]


class Animation(Protocol):
    def run(self) -> animation_return: ...


class FillColour(Animation):
    def __init__(self, colour: tuple[int, int, int]):
        self.colour = colour

    def run(self) -> animation_return:
        while 1:
            yield Fill(self.colour)
            yield Delay(0.01)


class FlashAnimation(Animation):
    def __init__(
        self,
        colour: tuple[int, int, int] | None = None,
        min_brightness: float = 0.3,
        delay: float = 0.001,
    ):
        self.colour = colour or (255, 255, 255)
        self.min_brightness = min_brightness
        self.delay = delay

    def set_get_colour(self, index: int) -> tuple[int, int, int]:
        brightness: float = index / 255
        if brightness < self.min_brightness:
            brightness = self.min_brightness

        # Convert RGB to HSV, adjust brightness, convert back
        red, green, blue = scale_brightness(self.colour, brightness)

        colour = (red, green, blue)
        logger.debug(f"Flashing colour: {colour}, brightness: {brightness}")
        return colour

    def run(self) -> animation_return:
        min_index = int(self.min_brightness * 255)
        while True:
            for i in range(255, min_index, -1):
                yield Fill(self.set_get_colour(i))
                yield Delay(self.delay)
            for i in range(min_index, 255):
                yield Fill(self.set_get_colour(i))
                yield Delay(self.delay)


class FlashAnimationFast(FlashAnimation):
    def __init__(self, colour: tuple[int, int, int] | None = None):
        super().__init__(colour, min_brightness=0.3, delay=0.0005)
