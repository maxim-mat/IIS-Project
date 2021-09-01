import mdptoolbox as mdptb
import numpy as np


class Robot(object):

    def __init__(self, states, initial, goal, r_actions, action_transition, h_actions=None, discount=0.9, max_iterations=10):
        if type(states) != list:
            raise ValueError("states must be list")
        if type(r_actions) != list:
            raise ValueError("robot actions must be list")
        if type(h_actions) != list:
            raise ValueError("human actions must be list")
        if goal not in states:
            raise ValueError("goal must be a state")
        if initial not in states:
            raise ValueError("initial must be a state")
        self.states = states
        self.r_actions = r_actions
        self.h_actions = h_actions if h_actions is not None else r_actions  # default symmetric actions
        self.action_transition = action_transition
        self.goal = goal
        self.initial = initial
        self.current = self.initial
        self.dr = discount
        self.idx_state = {i: s for i, s in enumerate(self.states)}
        self.state_idx = {v: k for k, v in self.idx_state.items()}
        self.idx_action = {i: s for i, s in enumerate(self.r_actions)}
        self.action_idx = {v: k for k, v in self.idx_action.items()}
        self.max_iter = int(max_iterations)
        # create base matrices
        self.T = np.zeros(shape=(len(self.r_actions), len(self.states), len(self.states)))
        for action in self.r_actions:
            a_idx = self.action_idx[action]
            for t_index, pre in enumerate(self.action_transition[action]["pre"]):
                for h_action in self.h_actions:
                    for ht_index, h_pre in enumerate(self.action_transition[h_action]["pre"]):
                        if h_pre == self.action_transition[action]["post"][t_index]:
                            self.T[a_idx, self.state_idx[pre], self.state_idx[self.action_transition[h_action]["post"][ht_index]]] = 1
        for i, ac in enumerate(self.T):
            for j, row in enumerate(ac):
                if row.sum() > 0:
                    self.T[i, j] /= row.sum()
                else:
                    self.T[i, j, 0] = 1
        self.R = np.zeros((len(self.states), len(self.r_actions)), dtype=float)
        self.R[self.state_idx[self.goal]] = 100
        self.policy = self.get_new_policy()
        #print(self.T[0])
        #print(self.T[4])
        print(self.policy)

    def get_new_policy(self):
        solver = mdptb.mdp.ValueIteration(self.T, self.R, self.dr)
        solver.run()
        return solver.policy

    def run(self, simulation):
        for n in range(self.max_iter):
            self.current = self.initial
            sequence, m_sequence = self.forward(simulation)
            self.update_T(sequence)
            self.update_R_msg(m_sequence)
            #simulation.set_flag() # should be 1 for human starting
            self.current = self.initial
            self.policy = self.get_new_policy()
            sequence_rotation, m_sequence_rotation = self.rotation(simulation)
            self.update_R(sequence_rotation)
            self.update_T_msg(m_sequence_rotation)
            self.policy = self.get_new_policy()
            simulation.next_click()

    def forward(self, sim):
        """
            each round on the sq should be an inner cell to work with update T
        """
        sq = []
        m_sq = []
        while self.current != self.goal:
            next_action = self.idx_action[self.policy[self.state_idx[self.current]]]
            print(next_action)
            sim.do_action(next_action)  # this apply the robot action
            #sim.root.after(1000, sim.do_action(next_action))
            end_state = None
            for p_post in range(0, len(self.action_transition[next_action]["post"])):
                if self.action_transition[next_action]["pre"][p_post] == self.current:
                    end_state = self.action_transition[next_action]["post"][p_post]
            if end_state == self.goal:
                break
            h_a, next_state = sim.get_action(), tuple(sim.get_state())  # apply the human action and update state
            h_msg = sim.get_message() # need to save
            for p_post in range(0, len(self.action_transition[next_action]["post"])):
                if self.action_transition[next_action]["pre"][p_post] == self.current:
                    s_state = self.action_transition[next_action]["post"][p_post]
            sim.send_robot_message(self.what_message_to_send(s_state, h_a, True))
            m_sq.append((self.current, next_action, h_msg))
            sq.append((self.current, next_action, h_a, next_state))
            self.current = next_state
            print(self.current)
        print(sq)
        print("exit forward")
        print(m_sq)
        return sq, m_sq

    def rotation(self, sim):
        """
        # 3. Set action a to observed human action.
        # 4. Sample robot action from T(current_state, a, next_state)
        # 5. Record current_state, a
        # 6. current_state = next_state
        :param sim:
        :return:
        """
        print("enter rotation")
        sq = []
        m_sq = []
        while self.current != self.goal:
            h_a, state = sim.get_action(), tuple(sim.get_state())
            h_msg = sim.get_message()
            sim.send_robot_message(self.what_message_to_send(self.current, h_a, False))
            if len(m_sq) > 0:
                m_sq[-1].append(h_msg)
            next_state_distrib = self.T[self.action_idx[h_a]][self.state_idx[self.current]]
            next_state_index = np.random.choice(range(len(next_state_distrib)), p=next_state_distrib)
            next_state = self.idx_state[next_state_index]
            m_sq.append([h_a, self.current, next_state])
            sq.append((self.current, h_a))
            for p_action in self.h_actions:
                for p_post in range(0, len(self.action_transition[p_action]["post"])):
                    if self.action_transition[p_action]["pre"][p_post] == state and self.action_transition[p_action]["post"][p_post] == next_state:
                        sim.do_action(p_action)
                        #sim.root.after(1000, sim.do_action(p_action))
                        print(state)
                        print(p_action)
            self.current = next_state
        if len(m_sq) > 0:
            m_sq[-1].append(None)
        print(sq)
        print("exit rotation")
        print(m_sq)
        return sq, m_sq

    def update_T(self, sq):
        """
            the added probability weight can be adjusted to frequncies
        """
        for state, r_action, h_action, state_star in sq:
            self.T[self.action_idx[r_action]][self.state_idx[state]][self.state_idx[state_star]] += 1.0
            self.T[self.action_idx[r_action]][self.state_idx[state]] = self.T[self.action_idx[r_action]][self.state_idx[state]] / sum(self.T[self.action_idx[r_action]][self.state_idx[state]])
        return

    def update_R(self, sq):
        """
            The added reward to human chosen actions, can be more complex.
        """
        for state, h_action in sq:
            self.R[self.state_idx[state]][self.action_idx[h_action]] += 1
        return

    def update_T_msg(self, m_sq):
        for h_a_q, state_q, state_star_q, human_msg_q in m_sq:
            if human_msg_q is None:
                continue
            elif human_msg_q == "I approve this action":
                self.T[self.action_idx[h_a_q]][self.state_idx[state_q]][self.state_idx[state_star_q]] += 1.0
                self.T[self.action_idx[h_a_q]][self.state_idx[state_q]] = self.T[self.action_idx[h_a_q]][self.state_idx[state_q]] / sum(self.T[self.action_idx[h_a_q]][self.state_idx[state_q]])
            else:
                s_action = human_msg_q.split()
                del s_action[1:3]
                s_action[1] = int(s_action[1])
                s_action = tuple(s_action)
                s_state = None
                for p_post in range(0, len(self.action_transition[h_a_q]["post"])):
                    if self.action_transition[h_a_q]["pre"][p_post] == state_q:
                        s_state = self.action_transition[h_a_q]["post"][p_post]
                        continue
                for p_post in range(0, len(self.action_transition[s_action]["post"])):
                    if self.action_transition[s_action]["pre"][p_post] == s_state:
                        s_state = self.action_transition[s_action]["post"][p_post]
                        continue
                self.T[self.action_idx[h_a_q]][self.state_idx[state_q]][self.state_idx[s_state]] += 1.0
                self.T[self.action_idx[h_a_q]][self.state_idx[state_q]] = self.T[self.action_idx[h_a_q]][self.state_idx[state_q]] / sum(self.T[self.action_idx[h_a_q]][self.state_idx[state_q]])
        return

    def update_R_msg(self, m_sq):
        for state_q, action_q, human_msg_q in m_sq:
            if human_msg_q is None:
                continue
            elif human_msg_q == "I approve this action":
                self.R[self.state_idx[state_q]][self.action_idx[action_q]] += 1
            else:
                self.R[self.state_idx[state_q]][self.action_idx[action_q]] -= 1
                s_action = human_msg_q.split()
                del s_action[1:3]
                s_action[1] = int(s_action[1])
                s_action = tuple(s_action)
                self.R[self.state_idx[state_q]][self.action_idx[s_action]] += 1
        return

    def what_message_to_send(self, sub_state, observed_action, is_forward=True):
        if observed_action != ("wait", -1):
            return "Well done!"
        if is_forward:
            for p_action in self.h_actions:
                if p_action == ("wait", -1):
                    continue
                for p_post in range(0, len(self.action_transition[p_action]["post"])):
                    if self.action_transition[p_action]["pre"][p_post] == sub_state:
                        return "You could " + p_action[0] + " in " + str(p_action[1] + 1)
        else:
            for p_action in self.r_actions:
                if p_action == ("wait", -1):
                    continue
                for p_post in range(0, len(self.action_transition[p_action]["post"])):
                    if self.action_transition[p_action]["pre"][p_post] == sub_state:
                        return "You could " + p_action[0] + " in " + str(p_action[1] + 1)
        return


