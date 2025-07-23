import colorsys


def scale_brightness(
    colour: tuple[int, int, int], brightness: float
) -> tuple[int, int, int]:
    r, g, b = colour[0] / 255.0, colour[1] / 255.0, colour[2] / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    v = v * brightness  # Apply brightness to value component only
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)
