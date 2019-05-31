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

        self.inputBox = Text(self, height=1, width=50)
        self.inputBox.grid(row=0, column=0)

        self.loadButton = Button(self, text="LOAD INPUT", command=self.load)
        self.loadButton.grid(row=0, column=1)

        self.playButton = Button(self, text="PLAY", command=self.play)
        self.playButton.grid(row=0, column=2)

        self.pauseButton = Button(self, text="PAUSE", command=self.pause)
        self.pauseButton.grid(row=0, column=3)

        self.stepButton = Button(self, text="STEP", command=self.step)
        self.stepButton.grid(row=0, column=4)

        self.canvas = Canvas(self, width=400, height=100)
        self.canvas.grid(row=1, column=0, columnspan=4)

        self.canvas.create_polygon(190, 5, 210, 5, 200, 20)

        self.reset_tape()

        self.transitionBox = Text(self, width=50)
        self.transitionBox.grid(row=2, column=0)

        self.grid()

    def reset_tape(self, offset=0):
        self.canvas.delete("all")
        for i in range(-1, self.numBoxes+1):
            self.canvas.create_rectangle(self.bufferSize + self.boxSize * i + offset, 22, self.bufferSize + self.boxSize * (i + 1) + offset, 22 + self.boxSize)

    def display_tape(self, text, offset=0):
        self.reset_tape()
        for i in range(-1, min(self.numBoxes, len(text))+1):
            self.canvas.create_text(self.bufferSize + self.boxSize * (i+.5) + offset, 22+self.boxSize/2, text=text[i+1])

    def load(self):
        self.inputTape.set_input(self.inputBox.get("1.0", END))
        self.display_tape(self.inputTape.display_tape(self.numBoxes//2+1))
        self.display_tape([i for i in self.inputBox.get("1.0", END)])

    def move_tape(self, direction):
        pass
        # offset = 0
        # if direction == LEFT:
        #     while offset <

    def play(self):
        pass

    def pause(self):
        pass

    def step(self):
        self.pause()

root = Tk()
app = Application(root)
root.mainloop()