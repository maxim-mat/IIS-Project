import mdptoolbox as mdptb
import numpy as np


def create_dict_to_index(container):
    return {k: i for i, k in enumerate(container)}


def create_mdp_T_R(states, robot_actions, human_actions, final_state):
    T = np.abs(np.random.normal(size=(len(robot_actions), len(states), len(states))))
    for i, ac in enumerate(T):
        for j, row in enumerate(ac):
            T[i, j] /= row.sum()
    R = np.ones((len(states), len(robot_actions)), dtype=float)

    # need to init R of final state to 100
    # need to represent human actions in T - need to calculate result as the result of both actions
    return T, R


def cross_train(T, R, Simulation=None):
    """
    0.9 discount used in paper
    :param T:
    :param R:
    :param Simulation:
    :return:
    """
    solver = mdptb.mdp.ValueIteration(T, R, 1)
    solver.run()
    pi = solver.policy
    print(pi)


def print_T(T, state_dict, actions_dict):
    print("state action")
    for s, v in state_dict.items():
        for a, va in actions_dict.items():
            print(s + ":    " + a +"    " + str(T[v][va]))
    return


class Robot(object):

    def __init__(self, states, initial, goal, r_actions, action_transition, h_actions=None, discount=1, max_iterations=10):
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
        self.max_iter = max_iterations
        # create base matrices
        self.T = np.zeros(shape=(len(self.r_actions), len(self.states), len(self.states)))
        for action in self.r_actions:
            a_idx = self.action_idx[action]
            for pre in self.action_transition[action]["pre"]:
                for post in self.action_transition[action]["post"]:
                    self.T[a_idx, self.state_idx[pre], self.state_idx[post]] = 1
        for i, ac in enumerate(self.T):
            for j, row in enumerate(ac):
                if row.sum() > 0:
                    self.T[i, j] /= row.sum()
                else:
                    self.T[i, j, 0] = 1
        self.R = np.zeros((len(self.states), len(self.r_actions)), dtype=float)
        self.R[self.state_idx[self.goal]] = 100
        self.policy = self.get_new_policy()
        print(self.policy)

    def get_new_policy(self):
        solver = mdptb.mdp.ValueIteration(self.T, self.R, self.dr)
        solver.run()
        return solver.policy

    def run(self, simulation):
        for _ in range(self.max_iter):
            sequence = self.forward(simulation)
            self.update_T(sequence)
            sequence_rotation = self.rotation(simulation)
            self.update_R(sequence_rotation)
            self.policy = self.get_new_policy()

    def forward(self, sim):
        """
            each round on the sq should be an inner cell to work with update T
        """
        sq = []
        while self.current != self.goal:
            print(self.current)
            next_action = self.idx_action[self.policy[self.state_idx[self.current]]]
            print(next_action)
            sq.append(next_action)
            sim.do_action(next_action)
            h_a, next_state = sim.get_action(), tuple(sim.get_state())
            # h_msg = sim.get_message()
            sq.extend([self.current, h_a, next_state])
            self.current = next_state
        print("exit forward")
        return sq

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
        h_a, state = sim.recieve()
        next_state_distrib = self.T[h_a][state]
        next_state_index = np.random.choice(range(len(next_state_distrib)), p=next_state_distrib)
        next_state = self.idx_state[next_state_index]
        sq.extend([state, h_a])
        sim.send(next_state)
        self.current = next_state
        print("exit rotation")
        return sq

    def update_T(self, sq):
        """
            the added probability weight can be adjusted to frequncies
        """
        for r_action, state, h_action, state_star in sq:
            self.T[r_action][state][state_star] += 1.0
            self.T[r_action][state] = self.T[r_action][state] / sum(self.T[r_action][state])
        return

    def update_R(self, sq):
        """
            The added reward to human chosen actions, can be more complex.
        """
        for state, h_action in sq:
            self.R[state][h_action] += 1
        return


if __name__ == '__main__':
    T, R = create_mdp_T_R(["a","b","c"], ["d", "w"], ["a"], 3)
    cross_train(T, R)
    # #print(T)
    # print(R)
    # state_dict = create_dict_to_index(["a","b","c"])
    # #print(state_dict)
    # robot_actions_dict = create_dict_to_index( ["d", "w"])
    # print_T(T, state_dict, robot_actions_dict)