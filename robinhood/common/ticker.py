from time import time

class Ticker:

    def __init__(self, tickrate_seconds):
        self.time = time()
        self.last_time = self.time
        self.delta = 0
        self.tickrate = tickrate_seconds

    def tick(self):
        self.last_time = self.time
        self.time = time()
        self.delta += self.time - self.last_time

        if self.delta > self.tickrate:
            self.delta = 0
            return True
        return False
