class Machine:
    def __init__(self, states, transition):
        pass

class State:
    def __init__(self):
        pass

class Transition:
    left = False
    right = True

    def __init__(self, start, end, read, write, direction):
        self.start = start
        self.end = end
        self.read = read
        self.write = write
        self.direction = direction