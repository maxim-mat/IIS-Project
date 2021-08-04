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

    def __init__(self, states, initial, goal, r_actions, h_actions=None, discount=1, max_iterations=10):
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
        self.goal = goal
        self.initial = initial
        self.current = self.initial
        self.dr = discount
        self.state_idx = {i: s for i, s in enumerate(self.states)}
        self.idx_state = {v: k for k, v in self.state_idx}
        self.action_idx = {i: s for i, s in enumerate(self.r_actions)}
        self.idx_action = {v: k for k, v in self.action_idx}
        self.max_iter = max_iterations
        # create base matrices
        self.T = np.abs(np.random.normal(size=(len(self.r_actions), len(self.states), len(self.states))))
        for i, ac in enumerate(self.T):
            for j, row in enumerate(ac):
                self.T[i, j] /= row.sum()
        self.R = np.ones((len(self.states), len(self.r_actions)), dtype=float)
        self.policy = self.get_new_policy()

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
    """
    each round on the sq should be an inner cell to work with update T
    """
    def forward(self, sim):
        sq = []
        while self.current != self.goal:
            next_action = self.idx_action[self.policy[self.state_idx[self.current]]]
            sq.append(next_action)
            sim.send(next_action)
            h_a, next_state = sim.recieve()
            sq.extend([self.current, h_a, next_state])
            self.current = next_state
        return sq

    def rotation(self, sim):
        sq = []
        # 3. Set action a to observed human action
        # 4. Sample robot action from T(current_state, a, next_state)
        # 5. Record current_state, a
        # 6. current_state = next_state
        return sq

    """
    the added probability weight can be adjusted to frequncies 
    """
    def update_T(self, sq):
        for r_action, state, h_action, state_star in sq:
            self.T[r_action][state][state_star] += 1.0
            self.T[r_action][state] = self.T[r_action][state]/ sum(self.T[r_action][state])
        return

    """
    The added reward to human chosen actions, can be more complex.
    """
    def update_R(self, sq):
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