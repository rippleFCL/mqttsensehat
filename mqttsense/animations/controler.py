from .animations import Animation, animation_return
from sense_hat import SenseHat
from threading import Thread, Event
from .drawables import Delay


class AnimationController:
    def __init__(self):
        self.sense = SenseHat()
        self.next_animation: animation_return | None = None
        self.next_animation_event = Event()
        self.display_thread = Thread(target=self.display_loop, daemon=True)
        self.display_thread.start()

    def run_animation(self, animation: animation_return):
        for drawable in animation:
            if isinstance(drawable, Delay):
                if self.next_animation_event.wait(drawable.seconds):
                    return
                continue
            drawable.draw(self.sense)


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
                    print(f"Error running animation: {e}")

    def set_animation(self, animation: Animation, *args):
        self.next_animation = animation.run(*args)
        self.next_animation_event.set()
