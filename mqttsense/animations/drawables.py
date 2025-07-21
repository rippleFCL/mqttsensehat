from typing import Protocol
from venv import logger
from sense_hat import SenseHat
import logging

logger  = logging.getLogger(__name__)

class Drawable(Protocol):
    def draw(self, sense: SenseHat) -> None:
        """Draw the object on the Sense HAT."""


class Fill(Drawable):
    def __init__(self, color: tuple[int, int, int]):
        self.color = color

    def draw(self, sense: SenseHat) -> None:
        sense.clear(self.color)

class Pixel(Drawable):
    def __init__(self, x: int, y: int, color: tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color

    def draw(self, sense: SenseHat) -> None:
        sense.set_pixel(self.x, self.y, self.color)

class Board:
    def __init__(self):
        self.pixels: list[list[tuple[int, int, int]]] = [[(0, 0, 0) for _ in range(8)] for _ in range(8)]

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        if 0 <= x < 8 and 0 <= y < 8:
            self.pixels[y][x] = color

    @property
    def pixel_list(self) -> list[tuple[int, int, tuple[int, int, int]]]:
        return [(x, y, self.pixels[y][x]) for y in range(8) for x in range(8)]


class PixelGrid(Drawable):
    def __init__(self, pixels: Board):
        self.pixels = pixels

    def draw(self, sense: SenseHat) -> None:
        logger.debug(self.pixels.pixel_list)
        sense.set_pixels(self.pixels.pixel_list)

class Delay:
    def __init__(self, seconds: float):
        self.seconds = seconds
