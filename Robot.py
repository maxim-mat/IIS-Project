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


"""

Update transition matrix after forward phase 
improve estimation of human choice.

"""
def update_T(T, simulation_sequance):
    return


"""

Add constant value to R in the states reached by the human choice

"""
def update_R(R, simulation_sequance):
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