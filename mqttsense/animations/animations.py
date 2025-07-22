from typing import Any, Generator, Protocol
from .drawables import Drawable, Delay, Fill, Board, PixelGrid
import math
import logging
from .utils import scale_brightness

logger = logging.getLogger(__name__)

animation_return = Generator[Drawable | Delay, Any, None]




class Animation(Protocol):
    def run(self) -> animation_return: ...


class FillRainbow(Animation):
    def __init__(self, delay: float = 0.05):
        logger.debug(f"FillRainbow initialized with delay: {delay}")
        self.delay = delay

    def get_clr_by_angle(self, angle: float) -> int:
        return int(255 * abs((math.sin(math.radians(angle)))))

    def run(self) -> animation_return:
        index = 0
        while True:
            index += 1
            index %= 180
            red = self.get_clr_by_angle(index)
            green = self.get_clr_by_angle(index + 60)
            blue = self.get_clr_by_angle(index + 120)
            yield Fill((red, green, blue))
            yield Delay(self.delay)

class FillRainbowFast(FillRainbow):
    def __init__(self, delay: float = 0.01):
        super().__init__(delay)

class RollingRainbow(Animation):
    def __init__(self, delay: float = 0.05, width: int = 5):
        self.delay = delay
        self.width = width

    def get_clr_by_angle(self, angle: float) -> int:
        return int(255 * abs((math.sin(math.radians(angle)))))

    def run(self) -> animation_return:
        board = Board()
        index = 0
        while True:
            index += 1
            index %= 180
            for pixle in range(64):
                x = pixle % 8
                y = pixle // 8
                offset = (x + y) * self.width
                red = self.get_clr_by_angle(index + offset)
                green = self.get_clr_by_angle(index + offset + 60)
                blue = self.get_clr_by_angle(index + offset + 120)
                board.set_pixel(x, y, (red, green, blue))
            yield PixelGrid(board)
            yield Delay(self.delay)

class RollingRainbowFast(RollingRainbow):
    def __init__(self, delay: float = 0.01, width: int = 5):
        super().__init__(delay, width)



class FillColor(Animation):
    def __init__(self, color: tuple[int, int, int]):
        self.color = color

    def run(self) -> animation_return:
        while 1:
            yield Fill(self.color)
            yield Delay(0.01)


class FlashAnimation(Animation):
    def __init__(self, color: tuple[int, int, int] | None = None, min_brightness: float = 0.3, delay: float = 0.001):
        self.color = color or (255, 255, 255)
        self.min_brightness = min_brightness
        self.delay = delay

    def set_get_color(self, index: int) -> tuple[int, int, int]:
        brightness: float = index / 255
        if brightness < self.min_brightness:
            brightness = self.min_brightness

        # Convert RGB to HSV, adjust brightness, convert back
        red, green, blue = scale_brightness(self.color, brightness)

        color = (red, green, blue)
        logger.debug(f"Flashing color: {color}, brightness: {brightness}")
        return color

    def run(self) -> animation_return:
        min_index = int(self.min_brightness * 255)
        while True:
            for i in range(255, min_index, -1):
                yield Fill(self.set_get_color(i))
                yield Delay(self.delay)
            for i in range(min_index, 255):
                yield Fill(self.set_get_color(i))
                yield Delay(self.delay)

class FlashAnimationFast(FlashAnimation):
    def __init__(self, color: tuple[int, int, int] | None = None):
        super().__init__(color, min_brightness=0.3, delay=0.0005)
