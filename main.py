from tkinter import *
from machine import *

class Application(Frame):
    def __init__(self, master):
        super(Application, self).__init__(master)

        self.numBoxes = 9
        self.canvasWidth = 400
        self.canvasHeight = 100

        self.bufferSize = 5
        self.boxSize = (self.canvasWidth - self.bufferSize * 2) / self.numBoxes


        self.inputTape = Tape()
        self.machine = Machine()

        self.inputBox = Text(self, height=1, width=50)
        self.inputBox.grid(row=0, column=0)

        self.loadButton = Button(self, text="LOAD INPUT", command=self.load)
        self.loadButton.grid(row=0, column=1)

        self.playButton = Button(self, text="PLAY", command=self.left)
        self.playButton.grid(row=0, column=2)

        self.pauseButton = Button(self, text="PAUSE", command=self.right)
        self.pauseButton.grid(row=0, column=3)

        self.stepButton = Button(self, text="STEP", command=self.step)
        self.stepButton.grid(row=0, column=4)

        self.canvas = Canvas(self, width=400, height=100)
        self.canvas.grid(row=1, column=0, columnspan=4)

        self.reset_tape()

        Label(self, text="Start State", anchor='w').grid(row=2, column=0)

        self.start_state_box = Text(self, height=1, width=30)
        self.start_state_box.grid(row=3, column=0)

        Label(self, text="Transitions", anchor='w').grid(row=4, column=0)

        self.transitionBox = Text(self, height=10, width=30)
        self.transitionBox.grid(row=5, column=0)

        Label(self, text="End States", anchor='w').grid(row=6, column=0)

        self.end_state_box = Text(self, height=3, width=30)
        self.end_state_box.grid(row=7, column=0)

        self.start_state = ""
        self.final_states = []

        self.loadMachineButton = Button(self, text="LOAD MACHINE", command=self.loadMachine)
        self.loadMachineButton.grid(row=5, column=1)

        self.grid()

    def loadMachine(self):
        transitions = [t.split() for t in self.transitionBox.get("1.0", END).split("\n") if len(t) !=  0]
        self.start_state = self.start_state_box.get("1.0", END).strip()
        self.final_states = self.end_state_box.get("1.0", END).strip().split(" ")
        for i in range(len(transitions)):
            start, read, write, direction, end = transitions[i]
            self.machine.addTransition(Transition(start, read, write, direction, end))
        self.start_machine()

    def start_machine(self):
        current_state = self.start_state
        while current_state not in self.final_states:
            current_state = self.step(current_state)

    def step(self, state):
        pass

    def reset_tape(self, offset=0):
        self.canvas.delete("all")
        self.canvas.create_polygon(190, 5, 210, 5, 200, 20)
        for i in range(-2, self.numBoxes+2):
            self.canvas.create_rectangle(self.bufferSize + self.boxSize * i + offset, 22, self.bufferSize + self.boxSize * (i + 1) + offset, 22 + self.boxSize)

    def display_tape(self, text, offset=0):
        self.reset_tape(offset)
        for i in range(-2, min(self.numBoxes, len(text))+2):
            self.canvas.create_text(self.bufferSize + self.boxSize * (i+.5) + offset, 22+self.boxSize/2, text=text[i+2])
        self.canvas.update()

    def load(self):
        self.inputTape.set_input(self.inputBox.get("1.0", END)[:-1])
        self.display_tape(self.inputTape.display_tape(self.numBoxes//2+3))

    def left(self):
        self.move_tape(LEFT)
        self.inputTape.move_left()
        self.display_tape(self.inputTape.display_tape(self.numBoxes//2+3))

    def right(self):
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
        pass

    def pause(self):
        pass

    def step(self):
        self.pause()

root = Tk()
app = Application(root)
root.mainloop()