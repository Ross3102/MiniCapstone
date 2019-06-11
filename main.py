from tkinter import *
from machine import *
from random import randint
import math

NULL_CHAR = "~"


class ErrorWindow(Toplevel):
    def __init__(self, master, message):
        super(ErrorWindow, self).__init__(master)

        self.title("Error")

        Label(self, text=message).pack()
        Button(self, text="Dismiss", command=self.destroy).pack()


class ResultWindow(Toplevel):
    def __init__(self, master, message):
        super(ResultWindow, self).__init__(master)

        self.title("Result")

        Label(self, text=message).pack()
        Button(self, text="Dismiss", command=self.destroy).pack()


class NameState(Toplevel):
    def __init__(self, builder, dragging_state, states_list):
        super(NameState, self).__init__(builder.master)

        self.title("New State")

        self.builder = builder
        self.dragging_state = dragging_state
        self.states_list = states_list

        Label(self, anchor=W, text="State Name: ").grid(row=0, column=0)
        self.name_text = Text(self, height=1, width=8)
        self.name_text.grid(row=0, column=1)

        Button(self, text="CONFIRM", command=self.get_name).grid(row=1, column=0)
        Button(self, text="CANCEL", command=self.delete).grid(row=1, column=1)

    def get_name(self):
        name = self.name_text.get("1.0", END).strip()
        self.dragging_state.name = name
        self.states_list.append(self.dragging_state)
        self.builder.redraw()
        self.destroy()

    def delete(self):
        self.destroy()


class TransitionCreator(Toplevel):
    def __init__(self, builder, start_state, end_state):
        super(TransitionCreator, self).__init__(builder.master)

        self.title("New Transition")

        self.builder = builder

        self.start_state = start_state
        self.end_state = end_state

        Label(self, anchor=W, text="From: ").grid(row=0, column=0)
        Label(self, text=start_state.name).grid(row=0, column=1)

        Label(self, anchor=W, text="Read: ").grid(row=1, column=0)
        self.read_text = Text(self, height=1, width=5)
        self.read_text.grid(row=1, column=1)

        Label(self, anchor=W, text="Write: ").grid(row=2, column=0)
        self.write_text = Text(self, height=1, width=5)
        self.write_text.grid(row=2,column=1)

        Label(self, anchor=W, text="Direction: ").grid(row=3, column=0)
        self.direction_text = Text(self, height=1, width=5)
        self.direction_text.grid(row=3, column=1)

        Label(self, anchor=W, text="To: ").grid(row=4, column=0)
        Label(self, text=end_state.name).grid(row=4,column=1)

        Button(self, text="MAKE TRANSITION", command=self.make_transition).grid(row=5, column=0)
        Button(self, text="CANCEL", command=self.destroy).grid(row=5,column=1)

    def make_transition(self):
        read = self.read_text.get("1.0", END).strip()
        write = self.write_text.get("1.0", END).strip()
        direction = self.direction_text.get("1.0", END).strip()
        self.start_state.addTransition(Transition(read, write, direction, self.end_state))
        self.builder.redraw()
        self.destroy()


class Builder(Toplevel):
    def __init__(self, runner, old_machine=None):
        super(Builder, self).__init__(runner.master)

        self.title("Turing Machine Builder")

        self.runner = runner

        self.canvas = Canvas(self, width=1000, height=600)
        self.canvas.grid(row=0, column=0)
        Button(self, text="FINISH BUILDING", command=self.finish).grid(row=1, column=0)

        self.states = []
        self.start_state = None
        self.end_states = []

        self.mouse = False
        self.mousepos = [0, 0]
        self.draggingState = None

        self.transitioning = None

        self.bind('<ButtonPress-1>', self.mouse_clicked)
        self.bind('<ButtonRelease-1>', self.mouse_released)
        self.bind("<Motion>", self.mouse_moved)
        self.bind("<Double-Button-1>", self.modify_state_start)
        self.bind("<ButtonPress-2>", self.modify_state_end)

        self.draw_side_menu()

        if old_machine is not None:
            for s in old_machine.states.values():
                newState = LocationState(s.name, randint(185,950), randint(65,550))
                self.states.append(newState)
                if s.name == old_machine.start_state_name:
                    self.start_state = s.name
                if s.name in old_machine.final_state_names:
                    self.end_states.append(s.name)

            for oldstate in old_machine.states.values():
                s1 = None
                for s in self.states:
                    if oldstate.name == s.name:
                        s1 = s
                for t in oldstate.transitions:
                    for s2 in self.states:
                        if s2.name == t.end.name:
                            s1.addTransition(Transition(t.read, t.write, t.direction, s2))

        self.redraw()

    def open_transition_window(self, start, end):
        self.transition_creator = TransitionCreator(self, start, end)

    def in_circle(self, x, y, cx, cy, r):
        return math.sqrt((cx-x)**2+(cy-y)**2) <= r

    def in_rect(self, x, y, lx, ty, rx, by):
        return lx <= x <= rx and ty <= y <= by

    def mouse_clicked(self, event):
        self.mouse = True
        if self.in_circle(event.x, event.y, 45, 45, 35):
            self.draggingState = LocationState("", event.x, event.y)
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
                        self.open_transition_window(self.transitioning, circle)
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
                if self.draggingState.name in self.end_states:
                    self.end_states.remove(self.draggingState.name)
                if self.draggingState == self.start_state:
                    self.start_state = None
            else:
                if self.draggingState.name == "":
                    name_menu = NameState(self, self.draggingState, self.states)
                else:
                    self.states.append(self.draggingState)

        self.draggingState = None
        self.redraw()

    def modify_state_start(self, event):
        for s in self.states:
            if self.in_circle(event.x, event.y, s.x, s.y, 35):
                if self.start_state == s.name:
                    self.start_state = None
                else:
                    self.start_state = s.name
        self.redraw()

    def modify_state_end(self, event):
        for s in self.states:
            if self.in_circle(event.x, event.y, s.x, s.y, 35):
                if s.name in self.end_states:
                    self.end_states.remove(s.name)
                else:
                    self.end_states.append(s.name)
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        self.draw_side_menu()

        for s in self.states + ([self.draggingState] if self.draggingState is not None else []):
            if self.transitioning is not None:
                color = "blue"
            elif s.name == self.start_state:
                color = "green"
            else:
                color = "black"
            self.canvas.create_oval(s.x - 35, s.y - 35, s.x + 35, s.y + 35, outline=color)
            if s.name in self.end_states:
                self.canvas.create_oval(s.x - 30, s.y - 30, s.x + 30, s.y + 30, outline=color)
            self.canvas.create_text(s.x, s.y, text=s.name, fill=color)
            end_list = []
            for t in s.transitions:
                if t.end.y == s.y and t.end.x == s.x:
                    modifier_x = 1
                    modifier_y = 1
                    x = s.x
                    y = s.y + modifier_y * 15 * (end_list.count(t.end.name) + 1)
                    arrow_start_x = s.x
                    arrow_start_y = s.y
                    arrow_x = t.end.x
                    arrow_y = t.end.y
                elif abs(t.end.y) == abs(s.y):
                    if t.end.x > s.x:
                        modifier_x = 0
                        modifier_y = -1
                        arrow_start_x = s.x + 35
                        arrow_x = t.end.x - 35
                    else:
                        modifier_x = 0
                        modifier_y = 1
                        arrow_start_x = s.x - 35
                        arrow_x = t.end.x + 35

                    x = (s.x + t.end.x) / 2
                    y = s.y + modifier_y * 15 * (end_list.count(t.end.name) + 1)
                    arrow_start_y = s.y
                    arrow_y = t.end.y

                elif abs(t.end.x) == abs(s.x):
                    if t.end.y > s.y:
                        modifier_x = 1
                        modifier_y = 0
                        arrow_start_y = s.y + 35
                        arrow_y = t.end.y - 35
                    else:
                        modifier_x = -1
                        modifier_y = 0
                        arrow_start_y = s.y - 35
                        arrow_y = t.end.y + 35

                    x = s.x + modifier_x * 15 * (end_list.count(t.end.name) + 1)
                    y = (s.y + t.end.y) / 2
                    arrow_start_x = s.x
                    arrow_x = t.end.x

                else:
                    slope = -1 * (t.end.x - s.x)/(t.end.y - s.y)
                    arrow_slope = (s.y - t.end.y) / (s.x - t.end.x)
                    if t.end.x - s.x < 0:
                        if t.end.y - s.y < 0:
                            modifier_y = 1
                            modifier_x = -1
                        else:
                            modifier_y = 1
                            modifier_x = 1
                        arrow_start_y = 35 * -arrow_slope / math.sqrt(arrow_slope ** 2 + 1) + s.y
                        arrow_y = 35 * arrow_slope / math.sqrt(arrow_slope ** 2 + 1) + t.end.y
                    else:
                        if t.end.y - s.y < 0:
                            modifier_y = -1
                            modifier_x = -1
                        else:
                            modifier_y = -1
                            modifier_x = 1
                        arrow_start_y = 35 * arrow_slope / math.sqrt(arrow_slope ** 2 + 1) + s.y
                        arrow_y = -35 * arrow_slope / math.sqrt(arrow_slope ** 2 + 1) + t.end.y

                    y = modifier_y * 15 * (end_list.count(t.end.name) + 1) * abs(slope) / math.sqrt(slope ** 2 + 1) + (t.end.y + s.y) / 2
                    x = (y - (t.end.y + s.y) / 2) / slope + (t.end.x + s.x) / 2
                    arrow_start_x = (arrow_start_y - s.y) / arrow_slope + s.x
                    arrow_x = (arrow_y - t.end.y) / arrow_slope + t.end.x

                end_list.append(t.end.name)

                arrow_start_x += modifier_x * 3
                arrow_x += modifier_x * 3
                arrow_start_y += modifier_y * 3
                arrow_y += modifier_y * 3

                if t.end == s:
                    self.canvas.create_arc(s.x, s.y-35, s.x - 70, s.y + 35, extent=242, style=ARC, start=60)
                    self.canvas.create_text(x, s.y-(25 + 15*(end_list.count(s.name) + 1)), text=str(t))
                    top_point_x = s.x-35+35*math.cos(math.radians(60))
                    top_point_y = s.y - 35*math.sin(math.radians(60))
                    tangent_slope = top_point_y/top_point_x
                    self.canvas.create_line(top_point_x-1, top_point_y-tangent_slope, top_point_x, top_point_y, arrow=LAST)

                else:
                    self.canvas.create_line(arrow_start_x, arrow_start_y, arrow_x, arrow_y, arrow=LAST)
                    angle = math.atan2(s.y - t.end.y, t.end.x - s.x)*180/math.pi
                    if math.fabs(angle) > 90:
                        angle = angle + 180
                    self.canvas.create_text(x, y, text=str(t))
        if self.transitioning not in [True, None]:
            self.canvas.create_line(self.transitioning.x, self.transitioning.y, self.mousepos[0], self.mousepos[1])

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
        if self.start_state is None:
            e = ErrorWindow(self.runner.master, "The machine has no start state!")
            return
        elif len(self.end_states) == 0:
            e = ErrorWindow(self.runner.master, "The machine has no halt states!")
            return
        self.runner.start_state_box.delete('1.0', END)
        self.runner.start_state_box.insert("1.0", self.start_state)
        transition_text = ""
        for s in self.states:
            for i in s.transitions:
                transition_text = transition_text + s.name + i.text_str() + "\n"
        self.runner.transitionBox.delete('1.0', END)
        self.runner.transitionBox.insert("1.0", transition_text)
        final_state_text = ""
        for s in self.end_states:
            final_state_text = final_state_text + s + " "
        self.runner.end_state_box.delete('1.0', END)
        self.runner.end_state_box.insert("1.0", final_state_text)
        self.runner.load_machine()
        self.destroy()


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
        self.stepTimer = 0
        self.stepDelay = 13

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
        self.builder = Builder(self, self.machine)

    def reset(self):
        self.playButton.config(text="PLAY")
        self.current_state = self.machine.start_state()
        self.update_current_state(self.current_state.name)
        self.going = False
        self.correct = None

    def load_machine(self):
        transitions = [t.split() for t in self.transitionBox.get("1.0", END).split("\n") if len(t) != 0]

        start_state = self.start_state_box.get("1.0", END).strip()
        end_states = self.end_state_box.get("1.0", END).strip().split(" ")

        if start_state is None:
            e = ErrorWindow(self.master, "The machine has no start state!")
            return
        elif len(end_states) == 0:
            e = ErrorWindow(self.master, "The machine has no halt states!")
            return

        self.update_current_state(start_state)
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
        if self.stepTimer != 0:
            if self.stepTimer < 0:
                self.stepTimer -= 1
            else:
                self.stepTimer += 1
            if self.stepTimer % self.stepDelay == 0:
                self.display_tape(self.inputTape.display_tape(self.numBoxes // 2 + 3), self.stepTimer // self.stepDelay)
            if abs(self.stepTimer) >= self.stepDelay * self.boxSize:
                if self.stepTimer < 0:
                    self.inputTape.move_right()
                    self.display_tape(self.inputTape.display_tape(self.numBoxes // 2 + 3))
                else:
                    self.inputTape.move_left()
                    self.display_tape(self.inputTape.display_tape(self.numBoxes // 2 + 3))
                self.stepTimer = 0
        elif self.correct is None:
            if self.going:
                if not self.step():
                    self.correct = False
                    w = ResultWindow(self.master, "Input did not match!")
                    self.playButton.config(text="RESET")
            if self.current_state is not None and self.current_state.name in self.machine.final_state_names:
                self.correct = True
                w = ResultWindow(self.master, "Input matched!")
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
            letter = "" if text[i+2] == "~" else text[i+2]
            self.canvas.create_text(self.bufferSize + self.boxSize * (i+.5) + offset, 22+self.boxSize/2, text=letter)
        self.canvas.update()

    def load(self):
        if self.machine.start_state() is None:
            e = ErrorWindow(self.master, "You must create a machine before loading input!")
            return
        self.reset()
        self.inputTape.set_input(self.inputBox.get("1.0", END)[:-1])
        self.display_tape(self.inputTape.display_tape(self.numBoxes//2+3))

    def left(self):
        self.display_tape(self.inputTape.display_tape(self.numBoxes // 2 + 3))
        self.move_tape(LEFT)

    def right(self):
        self.display_tape(self.inputTape.display_tape(self.numBoxes // 2 + 3))
        self.move_tape(RIGHT)

    def move_tape(self, direction):
        if direction == LEFT:
            self.stepTimer = 1
        else:
            self.stepTimer = -1

    def play(self):
        if self.current_state is None:
            e = ErrorWindow(self.master, "You cannot run without loading a machine!")
            return
        if self.correct is not None:
            self.load()
        else:
            self.going = True

    def pause(self):
        self.going = False

    def step_button_pressed(self):
        if self.current_state is None:
            e = ErrorWindow(self.master, "You cannot run without loading a machine!")
            return
        self.pause()
        if self.stepTimer == 0 and self.correct is None and not self.step():
            self.correct = False
            w = ResultWindow(self.master, "Input did not match!")
            self.playButton.config(text="RESET")

root = Tk()
root.title("Turing Machine Runner")
app = Runner(root)
root.mainloop()