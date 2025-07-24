from math import cos, radians, sin


class RollingRainbowOffset:
    def __init__(self, width: int = 5):
        self.width = width

    def __call__(self, x: int, y: int) -> float:
        return (x + y) * self.width


class FillRainbowOffset:
    def __init__(self): ...

    def __call__(self, x: int, y: int) -> float:
        # For FillRainbow, we can return a constant offset or a simple function
        return 0.0


class CircleRainbowOffset:
    def __init__(self, x_middle: float = 4.5, y_middle: float = 4.5, scale: float = 5):
        self.x_middle = x_middle
        self.y_middle = y_middle
        self.scale = scale

    def __call__(self, x: int, y: int) -> float:
        # For Circles, we can return an offset based on the distance from the center
        return (
            ((x - self.x_middle) ** 2 + (y - self.y_middle) ** 2) ** 0.5
        ) * self.scale


class SpinRainbowOffset:
    def __init__(self, speed: float = 1):
        self.speed = speed
        self.angle = 0

    def __call__(self, x: int, y: int) -> float:
        # For SpinRainbow, we can return an offset based on the angle from the center
        offset = x * cos(radians(self.angle)) + y * sin(radians(self.angle))
        self.angle += self.speed
        self.angle %= 360
        return offset
