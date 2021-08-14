from tkinter import *
from Robot import Robot


class Interface:
    def __init__(self):
        # possible states: None, 'drill', 'place_screw', 'screw'
        self.state = [None, None, None]

        # Ordered from the left screw to the right screw
        self.valid_actions = {'drill': [True, True, True],
                              'place_screw': [False, False, False],
                              'screw': [False, False, False]}

        self.iteration = 1
        self.phase = 'forward'
        self.turn = 'Robot'
        self.last_human_action = None

        self.root = Tk()

        # define interface
        self.iterations = 5
        self.middle_frame = Frame(self.root)
        self.bottom_frame = Frame(self.root)
        self.side_frame = Frame(self.root)
        self.balance_frame = Frame(self.root)
        self.next_frame = Frame(self.root)

        self.middle_frame.grid(row=0, column=3, padx=70, pady=15)
        self.bottom_frame.grid(row=1, column=3, padx=70, pady=15)
        self.side_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=30)
        self.balance_frame.grid(row=0, column=5, columnspan=2, padx=20, pady=30)
        self.next_frame.grid(row=2, column=4, pady=10)

        # ask for a number of iterations
        self.num_iter_label = Label(self.middle_frame, text=f"please set a number of iterations\n")
        self.num_iter_label.grid(row=0, column=0)

        self.iterations_input = Entry(self.middle_frame)
        self.iterations_input.grid(row=2, column=0, padx=5)
        self.iterations_input.insert(0, f"{self.iterations}")

        self.img = PhotoImage(file="images/full_table.png")  # load the image
        self.canvas = Canvas(self.middle_frame, width=self.img.width(), height=self.img.height(), borderwidth=0)

        # continue button
        self.continue_button = Button(self.bottom_frame, text="continue", padx=30, pady=10, command=self.continue_click)
        self.continue_button.grid(row=3, column=0)

        self.screws = {}

        self.flag = IntVar(0)

        self.space = Label(self.middle_frame, text="", font=("Arial", 18))
        self.space.grid(row=4, column=0)

        # action buttons
        self.drill1 = Button(self.bottom_frame, text="drill", padx=30, pady=10, command=lambda: self.drill_click(0))
        self.drill2 = Button(self.bottom_frame, text="drill", padx=30, pady=10, command=lambda: self.drill_click(1))
        self.drill3 = Button(self.bottom_frame, text="drill", padx=30, pady=10, command=lambda: self.drill_click(2))
        self.place1 = Button(self.bottom_frame, text="place\nscrew", padx=30, pady=10, command=lambda: self.place_click(0, self.screws))
        self.place2 = Button(self.bottom_frame, text="place\nscrew", padx=30, pady=10, command=lambda: self.place_click(1, self.screws))
        self.place3 = Button(self.bottom_frame, text="place\nscrew", padx=30, pady=10, command=lambda: self.place_click(2, self.screws))
        self.screw1 = Button(self.bottom_frame, text="screw", padx=30, pady=10, command=lambda: self.screw_click(0, self.screws))
        self.screw2 = Button(self.bottom_frame, text="screw", padx=30, pady=10, command=lambda: self.screw_click(1, self.screws))
        self.screw3 = Button(self.bottom_frame, text="screw", padx=30, pady=10, command=lambda: self.screw_click(2, self.screws))

        self.next_phase = Button(self.next_frame, text='next phase', pady=10, command=lambda: self.next_click())

        l = [None, "drill", "place_screw", "screw"]
        states = [(x, y, z) for x in l for y in l for z in l]
        initial = (None, None, None)
        goal = ("screw", "screw", "screw")
        actions = ["drill", "place_screw", "screw"]
        robot_actions = [("drill", x) for x in range(len(self.state))] + [("screw", x) for x in range(len(self.state))]
        human_actions = [("place_screw", x) for x in range(len(self.state))]
        action_transition = {}
        action_precondition = {"drill": None, "place_screw": "drill", "screw": "place_screw"}
        action_effect = {"drill": "drill", "place_screw": "place_screw", "screw": "screw"}
        for a_name, a_target in robot_actions:
            action_transition[(a_name, a_target)] = {"pre": [], "post": []}
            for state in states:
                if state[a_target] == action_precondition[a_name]:
                    action_transition[(a_name, a_target)]["pre"].append(state)
                if state[a_target] == action_effect[a_name]:
                    action_transition[(a_name, a_target)]["post"].append(state)

        self.robot = Robot(states, initial, goal, robot_actions, action_transition, human_actions)

        self.root.mainloop()

    # side frame stuff
    def set_side_frame(self):
        iteration_label = Label(self.side_frame, text=f"iteration: {self.iteration} out of {self.iterations}\n")
        turn_label = Label(self.side_frame, text=f"turn: {self.turn}\n")
        phase_label = Label(self.side_frame, text=f"phase: {self.phase}\n")
        iteration_label.grid(row=0, column=0)
        turn_label.grid(row=1, column=0)
        phase_label.grid(row=2, column=0)

    # button to continue to the simulation
    def continue_click(self):
        self.iterations = self.iterations_input.get()
        self.num_iter_label.grid_remove()
        self.iterations_input.grid_remove()
        self.continue_button.grid_remove()

        self.canvas.grid(row=0, column=0)
        self.canvas.create_image(0, 0, image=self.img, anchor=NW)

        self.set_side_frame()

        self.drill1.grid(row=0, column=0, ipadx=5, padx=70)
        self.drill2.grid(row=0, column=1, ipadx=5, padx=70)
        self.drill3.grid(row=0, column=2, ipadx=5, padx=70)
        self.place1.grid(row=1, column=0, padx=70)
        self.place2.grid(row=1, column=1, padx=70)
        self.place3.grid(row=1, column=2, padx=70)
        self.screw1.grid(row=2, column=0, padx=70)
        self.screw2.grid(row=2, column=1, padx=70)
        self.screw3.grid(row=2, column=2, padx=70)

        self.next_phase.grid(row=1, column=4)
        self.root.after(1000, self.call_backend)

    def next_click(self):
        self.canvas.grid_remove()

        self.canvas.grid(row=0, column=0)
        self.canvas.create_image(0, 0, image=self.img, anchor=NW)

        if self.phase == 'forward':
            self.phase = 'rotation'
            self.turn = 'Human'
            self.set_side_frame()
        elif self.phase == 'rotation':
            self.phase = 'forward'
            self.iteration += 1
            self.turn = 'Robot'
            self.set_side_frame()

        self.drill1.grid(row=0, column=0, ipadx=5, padx=70)
        self.drill2.grid(row=0, column=1, ipadx=5, padx=70)
        self.drill3.grid(row=0, column=2, ipadx=5, padx=70)
        self.place1.grid(row=1, column=0, padx=70)
        self.place2.grid(row=1, column=1, padx=70)
        self.place3.grid(row=1, column=2, padx=70)
        self.screw1.grid(row=2, column=0, padx=70)
        self.screw2.grid(row=2, column=1, padx=70)
        self.screw3.grid(row=2, column=2, padx=70)

        self.state = [None, None, None]
        self.valid_actions = {'drill': [True, True, True],
                              'place_screw': [False, False, False],
                              'screw': [False, False, False]}

    def drill_click(self, index):
        if self.valid_actions['drill'][index]:
            x1, y1 = get_coordinates(index)
            self.canvas.create_rectangle(x1, y1, x1 + 10, y1 + 40, outline="white", fill="white")
            if self.turn == 'Human':
                self.last_human_action = ('drill', index)
                self.turn = 'Robot'
                self.flag.set(1)
                self.set_side_frame()
            else:
                self.turn = 'Human'
                self.set_side_frame()

            self.valid_actions['place_screw'][index] = True
            self.valid_actions['drill'][index] = False

        else:
            warning_drill = Label(self.middle_frame, text="you can't drill here", font=("Arial", 18), fg="red")
            warning_drill.grid(row=4, column=0, ipadx=100)
            self.root.after(2000, lambda: warning_drill.destroy())

    def place_click(self, index, screws):
        if self.valid_actions['place_screw'][index]:
            x1, y2 = get_coordinates(index)
            screw = self.canvas.create_rectangle(x1, y2 - 40, x1 + 10, y2, outline="gray", fill="gray")
            screws[index] = screw
            if self.turn == 'Human':
                self.last_human_action = ('place_screw', index)
                self.turn = 'Robot'
                self.flag.set(1)
                self.set_side_frame()
            else:
                self.turn = 'Human'
                self.set_side_frame()

            self.valid_actions['screw'][index] = True
            self.valid_actions['place_screw'][index] = False
        else:
            warning_place = Label(self.middle_frame, text="you can't place a screw!", font=("Arial", 18), fg="red")
            warning_place.grid(row=4, column=0, ipadx=100)
            self.root.after(2000, lambda: warning_place.destroy())

    def screw_click(self, index, screws):
        if self.valid_actions['screw'][index]:
            self.canvas.delete(screws[index])
            x1, y1 = get_coordinates(index)
            self.canvas.create_rectangle(x1, y1, x1 + 10, y1 + 40, outline="gray", fill="gray")
            if self.turn == 'human':
                self.last_human_action = ('screw', index)
                self.turn = 'Robot'
                self.flag.set(1)
                self.set_side_frame()
            else:
                self.turn = 'Human'
                self.set_side_frame()

            self.valid_actions['screw'][index] = False
        else:
            warning_screw = Label(self.middle_frame, text="you can't screw the screw!", font=("Arial", 18), fg="red")
            warning_screw.grid(row=4, column=0)
            self.root.after(2000, lambda: warning_screw.destroy())

    # Takes an action of the robot and applies the relevant changes to the state
    # Input: action - tuple(action name, action index)
    # Output: state - dictionary of the states of all
    def do_action(self, action):
        # changing the state
        self.state[action[1]] = action[0]

        # visually change the interface and update the valid actions
        if action[0] == 'drill':
            self.drill_click(action[1])
        elif action[0] == 'place_screw':
            self.place_click(action[1], self.screws)
        elif action[0] == 'screw':
            self.screw_click(action[1], self.screws)

        self.flag.set(0)

    # Gets the action selected by the user
    # Input: No input
    # Output: action - tuple(action name, action index)
    def get_action(self):
        if not self.last_human_action:
            self.root.wait_variable(self.flag)
        action = self.last_human_action

        # changing the state
        self.state[action[1]] = action[0]               # set this according to the clicked button

        # changing the valid actions accordingly
        self.valid_actions[action[0]][action[1]] = False
        if action[0] == 'drill':
            self.valid_actions['place_screw'][action[1]] = True
        elif action[0] == 'place_screw':
            self.valid_actions['screw'][action[1]] = True

        self.last_human_action = None
        return action

    def get_state(self):
        return self.state

    def call_backend(self):
        self.robot.run(self)
        # self.do_action(('drill', 1))
        # print(self.get_action())
        # self.do_action(('drill', 0))
        # print(self.get_action())            # needs to be interface.root.after(1000, do_action(...)) on backend


# return the x,y coordinates of the left touch point with the table
def get_coordinates(index):
    y = 70
    if index == 0:
        x = 200
    elif index == 1:
        x = 440
    else:
        x = 680
    return x, y


if __name__ == "__main__":
    a = Interface()
