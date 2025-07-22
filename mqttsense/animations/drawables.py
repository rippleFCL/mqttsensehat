from typing import Protocol
from sense_hat import SenseHat
import logging
from .utils import scale_brightness

logger = logging.getLogger(__name__)


class Drawable(Protocol):
    def draw(self, sense: SenseHat, brightness: float) -> None:
        """Draw the object on the Sense HAT."""


class Fill(Drawable):
    def __init__(self, color: tuple[int, int, int]):
        self.color = color

    def draw(self, sense: SenseHat, brightness: float) -> None:
        scaled_color = scale_brightness(self.color, brightness)
        sense.clear(scaled_color)


class Pixel(Drawable):
    def __init__(self, x: int, y: int, color: tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color

    def draw(self, sense: SenseHat, brightness: float) -> None:
        scaled_color = scale_brightness(self.color, brightness)
        sense.set_pixel(self.x, self.y, scaled_color)


class Board:
    def __init__(self):
        self.pixels: list[list[tuple[int, int, int]]] = [[(0, 0, 0) for _ in range(8)] for _ in range(8)]

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        if 0 <= x < 8 and 0 <= y < 8:
            self.pixels[y][x] = color

    @property
    def pixel_list(self) -> list[tuple[int, int, int]]:
        return [(self.pixels[y][x]) for y in range(8) for x in range(8)]


class PixelGrid(Drawable):
    def __init__(self, pixels: Board):
        self.pixels = pixels

    def draw(self, sense: SenseHat, brightness: float) -> None:
        # Scale brightness for all pixels
        scaled_pixels = [scale_brightness(pixel, brightness) for pixel in self.pixels.pixel_list]
        logger.debug(scaled_pixels)
        sense.set_pixels(scaled_pixels)


class Delay:
    def __init__(self, seconds: float):
        self.seconds = seconds
