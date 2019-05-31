from tkinter import *

class Application(Frame):
    def __init__(self, master):
        super(Application, self).__init__(master)

        self.inputBox = Text(self, height=1, width=50)
        self.inputBox.grid(row=0, column=0)

        self.playButton = Button(self, text="PLAY", command=self.play)
        self.playButton.grid(row=0, column=1)

        self.pauseButton = Button(self, text="PAUSE", command=self.pause)
        self.pauseButton.grid(row=0, column=2)

        self.stepButton = Button(self, text="STEP", command=self.step)
        self.stepButton.grid(row=0, column=3)

        self.canvas = Canvas(self, width=400, height=100)
        self.canvas.grid(row=1, column=0, columnspan=4)

        self.canvas.create_polygon(190, 5, 210, 5, 200, 20)

        for i in range(9):
            self.canvas.create_rectangle(5+390/9*i, 22, 5+390/9*(i+1), 22+390/9)

        self.transitionBox = Text(self, width=50)
        self.transitionBox.grid(row=2, column=0)

        self.grid()

    def play(self):
        pass

    def pause(self):
        pass

    def step(self):
        self.pause()

root = Tk()
app = Application(root)
root.mainloop()