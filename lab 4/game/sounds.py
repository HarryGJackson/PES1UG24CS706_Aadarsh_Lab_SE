import math
from array import array

import pygame

# Sound effects
#
# The sounds are synthesised in code from simple sine tones, so the
# game doesn't need any audio files. If no audio device is available
# the game still runs, just silently.


class Sounds:
    def __init__(self):
        self.enabled = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.sample_rate, _, self.channels = pygame.mixer.get_init()
            self.enabled = True
        except pygame.error:
            return

        # Short, low "thud" for hitting a wall
        self.bounce = self._make([(180, 0.06)], volume=0.6, decay=40)
        # Rising C-E-G-C arpeggio for solving the maze
        self.win = self._make([(523, 0.1), (659, 0.1), (784, 0.1), (1047, 0.3)], volume=0.4, decay=6)
        # Falling "wah-wah-wah" for running out of time
        self.timeout = self._make([(392, 0.2), (349, 0.2), (294, 0.45)], volume=0.4, decay=4)

        self._last_bounce_ms = 0

    def _make(self, notes, volume, decay):
        # notes: list of (frequency in Hz, duration in seconds) played in order
        samples = array("h")
        for freq, duration in notes:
            count = int(self.sample_rate * duration)
            for i in range(count):
                t = i / self.sample_rate
                # quick fade-in to avoid clicks, then exponential fade-out
                envelope = min(1.0, i / 200) * math.exp(-decay * t)
                value = int(32767 * volume * envelope * math.sin(2 * math.pi * freq * t))
                samples.extend([value] * self.channels)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play_bounce(self, impact_speed):
        # Louder for harder hits; a short cooldown stops a marble that is
        # rattling against a wall from producing a constant buzz.
        if not self.enabled:
            return
        now = pygame.time.get_ticks()
        if now - self._last_bounce_ms < 80:
            return
        self._last_bounce_ms = now
        self.bounce.set_volume(min(1.0, 0.25 + impact_speed / 8))
        self.bounce.play()

    def play_win(self):
        if self.enabled:
            self.win.play()

    def play_timeout(self):
        if self.enabled:
            self.timeout.play()
