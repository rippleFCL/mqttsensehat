from typing import Any, Generator, Protocol
from .drawables import Drawable, Delay, Fill, Board, PixelGrid
import math
import logging

logger = logging.getLogger(__name__)

animation_return = Generator[Drawable | Delay, Any, None]


class Animation(Protocol):
    def run(self) -> animation_return: ...


class FillRainbow(Animation):
    def __init__(self, delay: float = 0.1):
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


class RollingRainbow(Animation):
    def __init__(self, delay: float = 0.001, width: int = 8):
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


class FillColor(Animation):
    def __init__(self, color: tuple[int, int, int]):
        self.color = color

    def run(self) -> animation_return:
        yield Fill(self.color)


class StopAnimation(Animation):
    def run(self) -> animation_return:
        yield Delay(0)

class FlashAnimation(Animation):
    def __init__(self, color: tuple[int, int, int] | None = None, min_brightness: float = 0, delay: float = 0.1):
        self.color = color or (255, 255, 255)
        self.min_brightness = min_brightness
        self.delay = delay

    def set_get_color(self, index: int) -> tuple[int, int, int]:
        brightness: float = index/255
        if brightness < self.min_brightness:
            brightness = self.min_brightness
        red = int(self.color[0] * brightness)
        green = int(self.color[1] * brightness)
        blue = int(self.color[2] * brightness)
        color = (red, green, blue)
        logger.debug(f"Flashing color: {color}, brightness: {brightness}")
        return color

    def run(self) -> animation_return:
        min_index = int(255 - (self.min_brightness * 255))
        while True:
            for i in range(255, min_index, -1):
                yield Fill(self.set_get_color(i))
                yield Delay(self.delay)
            for i in range(min_index, 255):
                yield Fill(self.set_get_color(i))
                yield Delay(self.delay)
