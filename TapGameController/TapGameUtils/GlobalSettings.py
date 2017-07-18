"""
This is a module that exports certain global runtime settings
"""
# -*- coding: utf-8 -*-

USE_ROS = True
USE_TEGA = True # if False, we are using Jibo

class TapGameLog(): # pylint: disable=too-few-public-methods
    """
    this is a mock class that allows tests to pass in a non-ROS environment
    """

    CHECK_IN = "CHECK_IN"
    GAME_START_PRESSED = "GAME_START_PRESSED"
    INIT_ROUND_DONE = "INIT_ROUND_DONE"
    START_ROUND_DONE = "START_ROUND_DONE"
    ROBOT_RING_IN = "ROBOT_RING_IN"
    PLAYER_RING_IN = "PLAYER_RING_IN"
    RESET_NEXT_ROUND_DONE = "RESET_NEXT_ROUND_DONE"
    SHOW_GAME_END_DONE = "SHOW_GAME_END_DONE"
    END_ROUND_DONE = "END_ROUND_DONE"
    SHOW_RESULTS_DONE = "SHOW_RESULTS_DONE"

    def __init__(self):
        pass

class TapGameCommand(): # pylint: disable=too-few-public-methods
    """
    this is a mock class that allows tests to pass in a non-ROS environment
    """

    INIT_ROUND = "INIT_ROUND"
    START_ROUND = "START_ROUND"
    ROBOT_RING_IN = "ROBOT_RING_IN"
    RESET_NEXT_ROUND = "RESET_NEXT_ROUND"
    SHOW_GAME_END = "SHOW_GAME_END"
    START_PRONUNCIATION_PANEL = "START_PRONUNCIATION_PANEL"
    SHOW_RESULTS = "START_PRONUNCIATION_PANEL"

    def __init__(self):
        pass


class TegaAction(): # pylint: disable=too-few-public-methods
    """
    this is a mock class for Tega Actions that allows tests to pass in a non-ROS environment
    """

    do_motion = True
    SILENT_CONFIRM = "SILENT_CONFIRM"

    def __init__(self):
        pass

class JiboAction(): # pylint: disable=too-few-public-methods
    """
    this is a mock class  for Jibo Actions that allows tests to pass in a non-ROS environment
    """

    do_motion = True
    SILENT_CONFIRM = "SILENT_CONFIRM"

