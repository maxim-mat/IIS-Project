from Robot import Robot
from layout import Interface


def main():
    l = [None, "drill", "place_screw", "screw"]
    states = [(x, y, z) for x in l for y in l for z in l]
    initial = (None, None, None)
    goal = ("screw", "screw", "screw")
    actions = ["drill", "place_screw", "screw"]
    robot_actions = ["drill", "screw"]
    human_actions = ["place_screw"]
    robot = Robot(states, initial, goal, robot_actions, human_actions)
    simulation = Interface()
    robot.run(simulation)


if __name__ == "__main__":
    main()
