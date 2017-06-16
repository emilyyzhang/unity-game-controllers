"""
This is a basic test config
"""
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import the module, then the class within the module
from TapGameController.TapGameFSM import TapGameFSM
from TapGameController.StudentModel import StudentModel
from TapGameController.TapGameUtils import Curriculum
