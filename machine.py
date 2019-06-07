LEFT = "<"
RIGHT = ">"

class Machine:
    def __init__(self):
        self.states = {}
        self.start_state_name = None
        self.final_state_names = []

    def start_state(self):
        if self.start_state_name is None:
            return None
        return self.states[self.start_state_name]

    def reset(self):
        self.states = {}
        self.start_state_name = None
        self.final_state_names = []

    def set_start_end(self, start, end):
        self.reset()
        for i in end:
            self.states[i] = State(i)
        self.states[start] = State(start)

        self.start_state_name = start
        self.final_state_names = end

    def addTransition(self, start, read, write, direction, end):
        end_state = self.states.get(end, None)
        if end_state is None:
            self.states[end] = State(end)
            end_state = self.states[end]

        start_state = self.states.get(start, None)
        if start_state is None:
            self.states[start] = State(start)
            start_state = self.states[start]

        start_state.addTransition(Transition(read, write, direction, end_state))



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
    def __init__(self, name):
        self.name = name
        self.transitions = []

    def addTransition(self, transition):
        self.transitions.append(transition)

    def transition(self, tape):
        for i in self.transitions:
            if i.get_read() == tape.get_current_input():
                tape.change_input(i.get_write(), i.get_read())
                if i.get_direction() == LEFT:
                    tape.move_left()
                elif i.get_direction() == RIGHT:
                    tape.move_right()
                return [i.get_direction(), i.get_end()]
        return False

class LocationState(State):
    def __init__(self, name, x, y):
        super(LocationState, self).__init__(name)
        self.x = x
        self.y = y

class Transition:
    def __init__(self, read, write, direction, end):
        self.end = end
        self.read = read
        self.write = write
        self.direction = direction

    def get_end(self):
        return self.end

    def get_read(self):
        return self.read

    def get_write(self):
        return self.write

    def get_direction(self):
        return self.direction

    def __str__(self):
        return "%s/%s %s %s" % (self.read, self.write, self.direction, self.end)