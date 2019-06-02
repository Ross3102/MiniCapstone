LEFT = False
RIGHT = True

class Machine:
    def __init__(self, states):
        self.states = states

class Tape:
    def __init__(self):
        self.right_stack = [None]
        self.left_stack = [None]

    def set_input(self, input):
        self.right_stack = [i for i in input[::-1]]
        self.left_stack = [None]

    def move_right(self):
        self.left_stack.append(self.right_stack.pop())
        if len(self.right_stack) == 0:
            self.right_stack.append(None)

    def move_left(self):
        self.right_stack.append(self.left_stack.pop())
        if len(self.left_stack) == 0:
            self.left_stack.append(None)

    def display_tape(self, num_elem):

        myList = [None for i in range(num_elem * 2 - 1)]

        for i in range(min(num_elem - 1, len(self.left_stack))):
            myList[num_elem-2-i] = self.left_stack[len(self.left_stack)-1-i]

        for i in range(min(num_elem, len(self.right_stack))):
            myList[num_elem-1+i] = self.right_stack[len(self.right_stack)-1-i]

        return myList

    def change_input(self, to_push, to_pop):
        if self.right_stack[-1] == to_pop:
            self.right_stack.pop()
            self.right_stack.append(to_push)

class State:
    def __init__(self, name, transitions):
        self.name = name
        self.transitions = transitions

    def transition(self, input, tape):
        for i in self.transitions:
            if i.start() == self.name and i.read() == input:
                tape.change_input(i.write(), i.read())
                if i.direction() == LEFT:
                    tape.move_left()
                else:
                    tape.move_right()

class Transition:
    def __init__(self, start, end, read, write, direction):
        self.start = start
        self.end = end
        self.read = read
        self.write = write
        self.direction = direction

    def start(self):
        return self.start

    def end(self):
        return self.end

    def read(self):
        return self.read

    def write(self):
        return self.write

    def direction(self):
        return self.direction