from tkinter import *
from machine import *
import math


class Builder(Toplevel):
    def __init__(self, runner):
        super(Builder, self).__init__(runner.master)

        self.runner = runner

        self.canvas = Canvas(self, width=1000, height=600)
        self.canvas.grid(row=0, column=0)
        Button(self, text="FINISH BUILDING", command=self.finish).grid(row=1, column=0)

        self.machine = Machine()
        self.states = []

        self.mouse = False
        self.mousepos = [0, 0]
        self.draggingState = None

        self.transitioning = None

        self.bind('<ButtonPress-1>', self.mouse_clicked)
        self.bind('<ButtonRelease-1>', self.mouse_released)
        self.bind("<Motion>", self.mouse_moved)

        self.draw_side_menu()

    def in_circle(self, x, y, cx, cy, r):
        return math.sqrt((cx-x)**2+(cy-y)**2) <= r

    def in_rect(self, x, y, lx, ty, rx, by):
        return lx <= x <= rx and ty <= y <= by

    def mouse_clicked(self, event):
        self.mouse = True
        if self.in_circle(event.x, event.y, 45, 45, 35):
            self.draggingState = LocationState("q0", event.x, event.y)
        elif self.in_rect(event.x, event.y, 10, 100, 120, 140):
            self.transitioning = True
        else:
            for s in range(len(self.states)):
                circle = self.states[s]
                if self.in_circle(event.x, event.y, circle.x, circle.y, 35):
                    if self.transitioning == True:
                        self.transitioning = circle
                        self.canvas.create_line(circle.x, circle.y, event.x, event.y)
                    elif self.transitioning is not None:
                        self.transitioning.addTransition(Transition("", "", ">", circle))
                        self.transitioning = None
                    else:
                        self.draggingState = self.states[s]
                        del self.states[s]
                    return
            if self.transitioning is not None:
                self.transitioning = None

    def mouse_released(self, event):
        self.mouse = False
        if self.draggingState is not None:
            if self.in_rect(event.x, event.y, 10, 160, 120, 580):
                 for s in self.states:
                    for t in s.transitions:
                        if t.end == self.draggingState:
                            s.transitions.remove(t)
            else:
                self.states.append(self.draggingState)

        self.draggingState = None
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        self.draw_side_menu()

        for s in self.states + ([self.draggingState] if self.draggingState is not None else []):
            color = "yellow" if self.transitioning is not None else "black"
            self.canvas.create_oval(s.x - 35, s.y - 35, s.x + 35, s.y + 35, outline=color)
            self.canvas.create_text(s.x, s.y, text=s.name, fill=color)
            for t in s.transitions:
                self.canvas.create_line(s.x, s.y, t.end.x, t.end.y)

        if self.transitioning not in [True, None]:
            self.canvas.create_line(self.transitioning.x, self.transitioning.y, self.mousepos[0], self.mousepos[1])
        # self.canvas.update()

    def mouse_moved(self, event):
        self.mousepos = [event.x, event.y]
        if self.draggingState is not None:
            self.draggingState.x = event.x
            self.draggingState.y = event.y
        self.redraw()

    def draw_side_menu(self):
        self.canvas.create_oval(10, 10, 80, 80)
        self.canvas.create_text(45, 45, text="New State")
        self.canvas.create_rectangle(10, 100, 120, 140)
        self.canvas.create_text(65, 120, text="New Transition")
        self.canvas.create_rectangle(10, 160, 120, 580, fill="red")
        self.canvas.create_text(65, 340, text="TRASH")

    def finish(self):
        pass


class Runner(Frame):
    def __init__(self, master):
        super(Runner, self).__init__(master)

        self.master = master

        self.numBoxes = 9
        self.canvasWidth = 400
        self.canvasHeight = 100

        self.bufferSize = 5
        self.boxSize = (self.canvasWidth - self.bufferSize * 2) / self.numBoxes

        self.going = False
        self.correct = None

        self.inputTape = Tape()
        self.machine = Machine()

        self.current_state = None

        self.inputBox = Text(self, height=1, width=50)
        self.inputBox.grid(row=0, column=0)

        Button(self, text="LOAD INPUT", command=self.load).grid(row=0, column=1)

        self.playButton = Button(self, text="PLAY", command=self.play)
        self.playButton.grid(row=0, column=2)

        Button(self, text="PAUSE", command=self.pause).grid(row=0, column=3)

        Button(self, text="STEP", command=self.step_button_pressed).grid(row=0, column=4)

        self.current_state_text = Label(self, text="Current State", height=2)
        self.current_state_text.grid(row=1, column=0)

        self.canvas = Canvas(self, width=400, height=100)
        self.canvas.grid(row=2, column=0, columnspan=4)

        Label(self, text="Start State").grid(row=3, column=0)

        self.start_state_box = Text(self, height=1, width=30)
        self.start_state_box.grid(row=4, column=0)

        Label(self, text="Transitions").grid(row=5, column=0)

        self.transitionBox = Text(self, height=10, width=30)
        self.transitionBox.grid(row=6, column=0)

        Label(self, text="End States").grid(row=7, column=0)

        self.end_state_box = Text(self, height=3, width=30)
        self.end_state_box.grid(row=8, column=0)

        self.loadMachineButton = Button(self, text="LOAD MACHINE", command=self.load_machine)
        self.loadMachineButton.grid(row=6, column=1)

        Button(self, text="LAUNCH MACHINE BUILDER", command=self.launch_builder).grid(row=7, column=1)

        self.erase_tape()
        self.grid()

        self.loop()

    def launch_builder(self):
        self.builder = Builder(self)

    def reset(self):
        self.playButton.config(text="PLAY")
        self.current_state = self.machine.start_state()
        self.update_current_state(self.current_state.name)
        self.going = False
        self.correct = None

    def load_machine(self):
        transitions = [t.split() for t in self.transitionBox.get("1.0", END).split("\n") if len(t) !=  0]

        start_state = self.start_state_box.get("1.0", END).strip()
        self.update_current_state(start_state)
        end_states = self.end_state_box.get("1.0", END).strip().split(" ")

        self.machine.set_start_end(start_state, end_states)
        for i in range(len(transitions)):
            start, read, write, direction, end = transitions[i]
            self.machine.addTransition(start, read, write, direction, end)

        self.load()
        self.reset()

    def update_current_state(self, text):
        self.current_state_text.destroy()
        self.current_state_text = Label(self, text="Current State: " + text, height=2)
        self.current_state_text.grid(row=1, column=0)

    def loop(self):
        if self.correct is None:
            if self.going:
                if not self.step():
                    self.correct = False
                    print("NO MATCH")
                    self.playButton.config(text="RESET")
            if self.current_state is not None and self.current_state.name in self.machine.final_state_names:
                self.correct = True
                print("MATCH")
                self.playButton.config(text="RESET")

        self.master.after(1, self.loop)

    def step(self):
        state_info = self.current_state.transition(self.inputTape)
        if not state_info:
            return False
        direction = state_info[0]
        self.current_state = state_info[1]
        self.update_current_state(self.current_state.name)
        if direction == LEFT:
            self.left()
        elif direction == RIGHT:
            self.right()
        return True

    def erase_tape(self, offset=0):
        self.canvas.delete("all")
        self.canvas.create_polygon(190, 5, 210, 5, 200, 20)
        for i in range(-2, self.numBoxes+2):
            self.canvas.create_rectangle(self.bufferSize + self.boxSize * i + offset, 22, self.bufferSize + self.boxSize * (i + 1) + offset, 22 + self.boxSize)

    def display_tape(self, text, offset=0):
        self.erase_tape(offset)
        for i in range(-2, min(self.numBoxes, len(text))+2):
            self.canvas.create_text(self.bufferSize + self.boxSize * (i+.5) + offset, 22+self.boxSize/2, text=text[i+2])
        self.canvas.update()

    def load(self):
        self.reset()
        self.inputTape.set_input(self.inputBox.get("1.0", END)[:-1])
        self.display_tape(self.inputTape.display_tape(self.numBoxes//2+3))

    def left(self):
        self.display_tape(self.inputTape.display_tape(self.numBoxes // 2 + 3))
        self.move_tape(LEFT)
        self.inputTape.move_left()
        self.display_tape(self.inputTape.display_tape(self.numBoxes//2+3))

    def right(self):
        self.display_tape(self.inputTape.display_tape(self.numBoxes // 2 + 3))
        self.move_tape(RIGHT)
        self.inputTape.move_right()
        self.display_tape(self.inputTape.display_tape(self.numBoxes // 2 + 3))

    def move_tape(self, direction):
        text = self.inputTape.display_tape(self.numBoxes // 2 + 3)
        offset = 0
        if direction == LEFT:
            while offset < self.boxSize:
                offset += 1
                self.display_tape(text, offset)
        else:
            while offset > -self.boxSize:
                offset -= 1
                self.display_tape(text, offset)

    def play(self):
        if self.correct is not None:
            self.load()
        else:
            self.going = True

    def pause(self):
        self.going = False

    def step_button_pressed(self):
        self.pause()
        if self.correct is None and not self.step():
            self.correct = False
            print("NO MATCH")
            return

root = Tk()
root.title("Turing Machine Runner")
app = Runner(root)
root.mainloop()