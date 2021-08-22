from tkinter import *
from Robot import Robot


class Interface:
    def __init__(self):
        # possible states: None, 'drill', 'place_screw', 'screw'
        self.state = [None, None, None]

        # Ordered from the left screw to the right screw
        self.valid_human_actions = {'drill': [False, False, False],
                                    'place_screw': [False, False, False],
                                    'screw': [False, False, False]}
        self.valid_robot_actions = {'drill': [True, True, True],
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
        self.chatbot_frame = Frame(self.root)
        self.balance_frame = Frame(self.root)
        self.next_frame = Frame(self.root)

        self.middle_frame.grid(row=0, column=3, padx=10, pady=15)
        self.bottom_frame.grid(row=1, column=3, padx=10, pady=20)
        self.side_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=30)
        self.balance_frame.grid(row=0, column=5, columnspan=2, padx=20, pady=30)
        self.next_frame.grid(row=2, column=3, pady=10)

        # ask for a number of iterations
        self.num_iter_label = Label(self.middle_frame, text=f"please set a number of iterations\n", font=("Calibri", 14))
        self.num_iter_label.grid(row=0, column=0)

        self.iterations_input = Entry(self.middle_frame)
        self.iterations_input.grid(row=2, column=0, padx=5, ipady=2)
        self.iterations_input.insert(0, f"{self.iterations}")

        self.img = PhotoImage(file="images/full_table.png")  # load the image
        self.drill_img = PhotoImage(file="images/drill_button.png")
        self.place_img = PhotoImage(file="images/place_button.png")
        self.screw_img = PhotoImage(file="images/screw_button.png")
        self.canvas = Canvas(self.middle_frame, width=self.img.width(), height=self.img.height(), borderwidth=0)

        # continue button
        self.continue_img = PhotoImage(file="images/continue_button.png")
        self.continue_button = Button(self.bottom_frame, image=self.continue_img, bd=0, padx=30, pady=10, command=self.continue_click)
        self.continue_button.grid(row=3, column=0)

        self.screws = {}

        self.flag = IntVar(0)

        self.space = Label(self.middle_frame, text="", font=("Arial", 15))
        self.space.grid(row=4, column=0)

        # action buttons
        self.drill1 = Button(self.bottom_frame, image=self.drill_img, bd=0, padx=10, pady=10, command=lambda: self.drill_click(0))
        self.drill2 = Button(self.bottom_frame, image=self.drill_img, bd=0, padx=10, pady=10, command=lambda: self.drill_click(1))
        self.drill3 = Button(self.bottom_frame, image=self.drill_img, bd=0, padx=10, pady=10, command=lambda: self.drill_click(2))
        self.place1 = Button(self.bottom_frame, image=self.place_img, bd=0, padx=10, pady=10, command=lambda: self.place_click(0, self.screws))
        self.place2 = Button(self.bottom_frame, image=self.place_img, bd=0, padx=10, pady=10, command=lambda: self.place_click(1, self.screws))
        self.place3 = Button(self.bottom_frame, image=self.place_img, bd=0, padx=10, pady=10, command=lambda: self.place_click(2, self.screws))
        self.screw1 = Button(self.bottom_frame, image=self.screw_img, bd=0, padx=10, pady=10, command=lambda: self.screw_click(0, self.screws))
        self.screw2 = Button(self.bottom_frame, image=self.screw_img, bd=0, padx=10, pady=10, command=lambda: self.screw_click(1, self.screws))
        self.screw3 = Button(self.bottom_frame, image=self.screw_img, bd=0, padx=10, pady=10, command=lambda: self.screw_click(2, self.screws))

        self.side_image = PhotoImage(file="images/side_frame_background.png")

        self.next_image = PhotoImage(file="images/next_button.png")
        self.next_phase = Button(self.next_frame, image=self.next_image, bd=0, command=lambda: self.next_click())
        self.skip_image = PhotoImage(file="images/skip_button.png")
        self.skip_turn = Button(self.next_frame, image=self.skip_image, bd=0, command=lambda: self.skip_click())

        self.scrollbar = Scrollbar(self.chatbot_frame)
        self.chat_history = Text(self.chatbot_frame, bd=1, bg="#d7dada", width="24", height="13", font=("Calibri", 14),
                            foreground="black", wrap=WORD, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.chat_history.yview)
        self.approve_img = PhotoImage(file="images/approve_button.png")
        self.reject_img = PhotoImage(file="images/reject_button.png")
        self.approve_button = Button(self.chatbot_frame, image=self.approve_img, bd=0,
                                command=lambda: self.chat_click("approve"))
        self.reject_button = Button(self.chatbot_frame, image=self.reject_img, bd=0,
                               command=lambda: self.chat_click("reject"))
        self.drill1_img = PhotoImage(file="images/drill_in_1_button.png")
        self.drill2_img = PhotoImage(file="images/drill_in_2_button.png")
        self.drill3_img = PhotoImage(file="images/drill_in_3_button.png")
        self.place1_img = PhotoImage(file="images/place_in_1_button.png")
        self.place2_img = PhotoImage(file="images/place_in_2_button.png")
        self.place3_img = PhotoImage(file="images/place_in_3_button.png")
        self.screw1_img = PhotoImage(file="images/screw_in_1_button.png")
        self.screw2_img = PhotoImage(file="images/screw_in_2_button.png")
        self.screw3_img = PhotoImage(file="images/screw_in_3_button.png")

        self.buttons = {}
        self.buttons[('drill', 0)] = Button(self.chatbot_frame, image=self.drill1_img, bd=0,
                                       command=lambda: self.send_suggestion("drill in place 1", True))
        self.buttons[('drill', 1)] = Button(self.chatbot_frame, image=self.drill2_img, bd=0,
                                       command=lambda: self.send_suggestion("drill in place 2", True))
        self.buttons[('drill', 2)] = Button(self.chatbot_frame, image=self.drill3_img, bd=0,
                                       command=lambda: self.send_suggestion("drill in place 3", True))
        self.buttons[('place', 0)] = Button(self.chatbot_frame, image=self.place1_img, bd=0,
                                       command=lambda: self.send_suggestion("place in hole 1", True))
        self.buttons[('place', 1)] = Button(self.chatbot_frame, image=self.place2_img, bd=0,
                                       command=lambda: self.send_suggestion("place in hole 2", True))
        self.buttons[('place', 2)] = Button(self.chatbot_frame, image=self.place3_img, bd=0,
                                       command=lambda: self.send_suggestion("place in hole 3", True))
        self.buttons[('screw', 0)] = Button(self.chatbot_frame, image=self.screw1_img, bd=0,
                                       command=lambda: self.send_suggestion("screw in the first screw", True))
        self.buttons[('screw', 1)] = Button(self.chatbot_frame, image=self.screw2_img, bd=0,
                                       command=lambda: self.send_suggestion("screw in the second screw", True))
        self.buttons[('screw', 2)] = Button(self.chatbot_frame, image=self.screw3_img, bd=0,
                                       command=lambda: self.send_suggestion("screw in the third screw", True))
        self.chat_history.tag_config('writer', foreground="#001889", font=("Calibri", 14, 'bold'))
        self.chat_history.tag_config('status', foreground="#001889", font=("Arial", 14))
        self.last_human_message = None

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
        space = Label(self.side_frame, text="", font=("Calibri", 1))
        space2 = Label(self.side_frame, text="", font=("Calibri", 20))
        image_label = Label(self.side_frame, image=self.side_image)
        iteration_label = Label(self.side_frame, text='iteration: ', font=('Calibri', 12, 'bold'))
        iteration_label_cont = Label(self.side_frame, text=f'{self.iteration} out of {self.iterations}\n', font=('Calibri', 12))
        turn_label = Label(self.side_frame, text='turn: ', font=('Calibri', 12, 'bold'))
        turn_label_cont = Label(self.side_frame, text=f'{self.turn}\n', font=('Calibri', 12))
        phase_label = Label(self.side_frame, text=f"phase: ", font=('Calibri', 12, 'bold'))
        phase_label_cont = Label(self.side_frame, text=f'{self.phase}\n', font=('Calibri', 12))
        space2.grid(row=0, column=0)
        image_label.grid(row=1, column=0, rowspan=8)
        space.grid(row=1, column=0)
        iteration_label.grid(row=2, column=0)
        iteration_label_cont.grid(row=3, column=0)
        turn_label.grid(row=4, column=0)
        turn_label_cont.grid(row=5, column=0)
        phase_label.grid(row=6, column=0)
        phase_label_cont.grid(row=7, column=0)

    # button to continue to the simulation
    def continue_click(self):
        self.iterations = self.iterations_input.get()
        self.num_iter_label.grid_remove()
        self.iterations_input.grid_remove()
        self.continue_button.grid_remove()
        self.space.grid_remove()

        self.canvas.grid(row=0, column=0)
        self.canvas.create_image(0, 0, image=self.img, anchor=NW)

        self.set_side_frame()

        self.drill1.grid(row=0, column=0, padx=70)
        self.drill2.grid(row=0, column=1, padx=70)
        self.drill3.grid(row=0, column=2, padx=70)
        self.place1.grid(row=1, column=0, padx=70)
        self.place2.grid(row=1, column=1, padx=70)
        self.place3.grid(row=1, column=2, padx=70)
        self.screw1.grid(row=2, column=0, padx=70)
        self.screw2.grid(row=2, column=1, padx=70)
        self.screw3.grid(row=2, column=2, padx=70)

        self.skip_turn.grid(row=1, column=4)
        self.next_phase.grid(row=1, column=5)

        self.root.after(1000, self.call_backend)
        self.chatbot()
        self.chat_history.insert(INSERT, f'iteration: {self.iteration}\nphase: {self.phase}\n\n', 'status')
        self.chat_history.see(INSERT)

    def next_click(self):
        self.canvas.grid_remove()

        self.canvas.grid(row=0, column=0)
        self.canvas.create_image(0, 0, image=self.img, anchor=NW)

        if self.phase == 'forward':
            self.flag.set(1)
            self.phase = 'rotation'
            self.turn = 'Human'
            self.set_side_frame()
            self.chat_history.insert(INSERT, '\n--------------------------------\n')
            self.chat_history.insert(INSERT, f'\niteration: {self.iteration}\nphase: {self.phase}\n\n', 'status')

            self.valid_human_actions = {'drill': [True, True, True],
                                        'place_screw': [False, False, False],
                                        'screw': [False, False, False]}
            self.valid_robot_actions = {'drill': [False, False, False],
                                        'place_screw': [False, False, False],
                                        'screw': [False, False, False]}

        elif self.phase == 'rotation':
            self.phase = 'forward'
            self.iteration += 1
            self.turn = 'Robot'
            self.set_side_frame()
            self.chat_history.insert(INSERT, '\n--------------------------------\n')
            self.chat_history.insert(INSERT, f'\niteration: {self.iteration}\nphase: {self.phase}\n\n', 'status')

            self.valid_human_actions = {'drill': [False, False, False],
                                        'place_screw': [False, False, False],
                                        'screw': [False, False, False]}
            self.valid_robot_actions = {'drill': [True, True, True],
                                        'place_screw': [False, False, False],
                                        'screw': [False, False, False]}
        self.chat_history.see(INSERT)

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

    def set_flag(self):
        self.flag.set(0)

    def skip_click(self):
        if self.turn == 'Human':
            self.turn = 'Robot'
            self.flag.set(1)
        else:
            self.turn = 'Human'
        self.set_side_frame()

    def drill_click(self, index):
        if self.turn == 'Human' and self.valid_human_actions['drill'][index]:
            x1, y1 = get_coordinates(index)
            self.canvas.create_rectangle(x1, y1, x1 + 10, y1 + 40, outline="#f0f0f0", fill="#f0f0f0")
            self.last_human_action = ('drill', index)
            self.turn = 'Robot'
            self.flag.set(1)
            self.set_side_frame()
            self.valid_robot_actions['place_screw'][index] = True
            self.valid_human_actions['drill'][index] = False

        elif self.turn == 'Robot' and self.valid_robot_actions['drill'][index]:
            x1, y1 = get_coordinates(index)
            self.canvas.create_rectangle(x1, y1, x1 + 10, y1 + 40, outline="#f0f0f0", fill="#f0f0f0")
            self.turn = 'Human'
            self.set_side_frame()

            self.valid_human_actions['place_screw'][index] = True
            self.valid_robot_actions['drill'][index] = False

        else:
            warning_drill = Label(self.middle_frame, text="you can't drill here", font=("Arial", 18), fg="red")
            warning_drill.grid(row=4, column=0, ipadx=100)
            self.root.after(2000, lambda: warning_drill.destroy())

    def place_click(self, index, screws):
        if self.turn == 'Human' and self.valid_human_actions['place_screw'][index]:
            x1, y2 = get_coordinates(index)
            screw = self.canvas.create_rectangle(x1, y2 - 40, x1 + 10, y2, outline="gray", fill="gray")
            screws[index] = screw
            self.last_human_action = ('place_screw', index)
            self.turn = 'Robot'
            self.flag.set(1)
            self.set_side_frame()
            self.valid_robot_actions['screw'][index] = True
            self.valid_human_actions['place_screw'][index] = False

        elif self.turn == 'Robot' and self.valid_robot_actions['place_screw'][index]:
            x1, y2 = get_coordinates(index)
            screw = self.canvas.create_rectangle(x1, y2 - 40, x1 + 10, y2, outline="gray", fill="gray")
            screws[index] = screw
            self.turn = 'Human'
            self.set_side_frame()
            self.valid_human_actions['screw'][index] = True
            self.valid_robot_actions['place_screw'][index] = False

        else:
            warning_place = Label(self.middle_frame, text="you can't place a screw!", font=("Arial", 18), fg="red")
            warning_place.grid(row=4, column=0, ipadx=100)
            self.root.after(2000, lambda: warning_place.destroy())

    def screw_click(self, index, screws):
        if self.turn == 'Human' and self.valid_human_actions['screw'][index]:
            self.canvas.delete(screws[index])
            x1, y1 = get_coordinates(index)
            self.canvas.create_rectangle(x1, y1, x1 + 10, y1 + 40, outline="gray", fill="gray")
            self.last_human_action = ('screw', index)
            self.turn = 'Robot'
            self.flag.set(1)
            self.set_side_frame()
            self.valid_human_actions['screw'][index] = False

        elif self.turn == 'Robot' and self.valid_robot_actions['screw'][index]:
            self.canvas.delete(screws[index])
            x1, y1 = get_coordinates(index)
            self.canvas.create_rectangle(x1, y1, x1 + 10, y1 + 40, outline="gray", fill="gray")
            self.turn = 'Human'
            self.set_side_frame()
            self.valid_robot_actions['screw'][index] = False

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

        if action is None:
            return action

        # changing the state
        self.state[action[1]] = action[0]               # set this according to the clicked button

        # changing the valid actions accordingly
        self.valid_human_actions[action[0]][action[1]] = False
        if action[0] == 'drill':
            self.valid_human_actions['place_screw'][action[1]] = True
        elif action[0] == 'place_screw':
            self.valid_human_actions['screw'][action[1]] = True

        self.last_human_action = None
        return action

    # function for the robot to send messages
    # input: message to send to human
    # output: no output
    def send_robot_message(self, message):
        self.chat_history.insert(INSERT, "Robot: ", 'writer')
        self.chat_history.insert(INSERT, f'{message}\n')

    def get_message(self):
        return self.last_human_message

    def get_state(self):
        return self.state

    def chatbot(self):
        self.balance_frame.grid_forget()
        self.chatbot_frame.grid(row=0, column=4, rowspan=3, padx=50, pady=100)
        self.chat_history.grid(row=0, column=0, columnspan=3)
        self.scrollbar.grid(row=0, column=4, ipady=110)
        self.approve_button.grid(row=1, column=0)
        self.reject_button.grid(row=2, column=0)

    def chat_click(self, button):
        if button == "approve":
            self.send_suggestion("I approve this action")
        elif button == "reject":
            self.send_suggestion("I reject this action")
            self.suggest_action()

        self.chat_history.see(INSERT)

    def suggest_action(self):
        self.approve_button.grid_forget()
        self.reject_button.grid_forget()
        global grided
        grided = []
        if self.phase == "forward":
            # drill in different place or screw in different place
            grid_row = 1
            for index in range(3):
                if self.valid_robot_actions['drill'][index]:
                    self.buttons[('drill', index)].grid(row=grid_row, column=0)
                    grided.append(('drill', index))
                    grid_row += 1
                if self.valid_robot_actions['screw'][index]:
                    self.buttons[('screw', index)].grid(row=grid_row, column=0)
                    grided.append(('screw', index))
                    grid_row += 1
        else:
            # place screw in different place
            for index in range(2):
                if self.valid_robot_actions['place'][index]:
                    self.buttons[('place', index)].grid(row=index+1, column=0)
                    grided.append(('place', index))

    def send_suggestion(self, message, remove=False):
        self.chat_history.insert(INSERT, 'You: ', 'writer')
        self.chat_history.insert(INSERT, f'{message}\n')
        self.last_human_message = message
        if remove:
            for i in grided:
                self.buttons[i].grid_forget()
            self.approve_button.grid(row=1, column=0)
            self.reject_button.grid(row=2, column=0)

    def call_backend(self):
        self.robot.run(self)


# return the x,y coordinates of the left touch point with the table
def get_coordinates(index):
    y = 70
    if index == 0:
        x = 140
    elif index == 1:
        x = 440
    else:
        x = 740
    return x, y


if __name__ == "__main__":
    a = Interface()