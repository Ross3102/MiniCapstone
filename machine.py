LEFT = False
RIGHT = True

class Machine:
    def __init__(self):
        self.states = []
        self.start_state = ""
        self.final_states = []

    def set_start_end(self, start, end):
        self.start_state = start
        self.final_states = end

    def addTransition(self, transition):
        if not transition.end in [s.name for s in self.states]:
            self.states.append(State(transition.end, []))

        for s in self.states:
            if transition.start == s.name:
                s.addTransition(transition)
                return

        self.states.append(State(transition.start, [transition]))

class Tape:
    def __init__(self):
        self.right_stack = [None]
        self.left_stack = [None]

    def get_current_input(self):
        return self.right_stack[-1]

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

    def addTransition(self, transition):
        self.transitions.append(transition)

    def transition(self, tape):
        for i in self.transitions:
            if i.start() == self.name and i.read() == tape.get_current_input():
                tape.change_input(i.write(), i.read())
                if i.direction() == LEFT:
                    tape.move_left()
                elif i.direction() == RIGHT:
                    tape.move_right()
                return [i.direction(), i.end()]

class Transition:
    def __init__(self, start, read, write, direction, end):
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