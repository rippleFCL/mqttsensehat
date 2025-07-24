import math
from typing import Callable

from mqttsense.animations.animation import Animation, animation_return
from mqttsense.animations.drawables import Board, Delay, PixelGrid


class Rainbow(Animation):
    def __init__(self, get_offset: Callable[[int, int], float], delay: float = 0.05):
        self.delay = delay
        self.get_offset = get_offset

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
                offset = self.get_offset(x, y)
                red = self.get_clr_by_angle(index + offset)
                green = self.get_clr_by_angle(index + offset + 60)
                blue = self.get_clr_by_angle(index + offset + 120)
                board.set_pixel(x, y, (red, green, blue))
            yield PixelGrid(board)
            yield Delay(self.delay)
