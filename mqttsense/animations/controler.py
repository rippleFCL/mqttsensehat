from .animations import Animation
from sense_hat import SenseHat
from threading import Thread, Event
from .drawables import Delay
import logging


logger = logging.getLogger(__name__)


class AnimationController:
    def __init__(self):
        self.sense = SenseHat()
        self.next_animation: Animation | None = None
        self.next_animation_event = Event()
        self.display_thread = Thread(target=self.display_loop, daemon=True)
        self.display_thread.start()
        self.brightness = 1

    def run_animation(self, animation: Animation):
        for drawable in animation.run():
            if isinstance(drawable, Delay):
                if self.next_animation_event.wait(drawable.seconds):
                    return
                continue
            drawable.draw(self.sense, self.brightness)

    def display_loop(self):
        while True:
            self.next_animation_event.wait()
            self.next_animation_event.clear()
            animation = self.next_animation
            self.next_animation = None
            if animation:
                try:
                    self.run_animation(animation)
                except Exception as e:
                    logger.exception(f"Error running animation: {e}")

    def set_animation(self, animation: Animation):
        self.next_animation = animation
        self.next_animation_event.set()
