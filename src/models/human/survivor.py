from .human import Human

class Survivor(Human):
    def __init__(self, id, x, y, rescued=False):
        super().__init__(id, x, y)
        self.rescued = rescued
    