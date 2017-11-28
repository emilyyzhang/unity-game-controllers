import time

from transitions import Machine
from .AgentModel import AgentModel
from .StudentModel import StudentModel
from .RobotBehaviorList import RobotBehaviors
from .RobotBehaviorList import RobotRoles
from .RobotBehaviorList import RobotRolesBehaviorsMap
from .RobotBehaviorList import RobotActionSequence as ras

# from GameUtils import Curriculum
from GameUtils import GlobalSettings
from GameUtils.GlobalSettings import iSpyGameStates as gs
from GameUtils.GlobalSettings import iSpyRobotInteractionStates as ris
from GameUtils.PronunciationUtils.PronunciationUtils import PronunciationUtils

if GlobalSettings.USE_ROS:
	from std_msgs.msg import Header  # standard ROS msg header
	from std_msgs.msg import String
	from unity_game_msgs.msg import iSpyCommand
	from unity_game_msgs.msg import iSpyAction

class ChildRobotInteractionFSM:
		'''
		child robot interaction FSM for robot's role switching project
		'''
		# class RobotActionSequence:
		# 	'''
		# 	robot action sequence for handling robot's actions for a given turn
		# 	'''
		# 	def __init__(self):
		# 		self.states =  [ras.TURN_STARTED, ras.SCREEN_MOVED, ras.OBJECT_FOUND, ras.OBJECT_CLICKED, 
		# 			ras.OBJECT_PRONOUNCED, ras.RESULTS_RETURNED, ras.TURN_FINISHED ]
		# 		self.transitions = [
		# 		 	{'trigger': ras.Triggers.NEXT, 'source': ras.TURN_STARTED, 'dest': ras.SCREEN_MOVED },
		# 		 	{'trigger': ras.Triggers.NEXT, 'source': ras.SCREEN_MOVED, 'dest': ras.OBJECT_FOUND},
		# 			{'trigger': ras.Triggers.NEXT, 'source': ras.OBJECT_FOUND, 'dest': ras.OBJECT_CLICKED },
		# 		 	{'trigger': ras.Triggers.NEXT, 'source': ras.OBJECT_CLICKED, 'dest': ras.OBJECT_PRONOUNCED},
		# 		 	{'trigger': ras.Triggers.NEXT, 'source': ras.OBJECT_PRONOUNCED, 'dest':  ras.RESULTS_RETURNED },
		# 		 	{'trigger': ras.Triggers.NEXT, 'source':  ras.RESULTS_RETURNED, 'dest': ras.TURN_FINISHED},
		# 		 	{'trigger': ras.Triggers.RESET, 'source':  ras.TURN_FINISHED, 'dest':ras.TURN_STARTED},
		# 		]
		# 		self.state_machine = Machine(self, states=self.states, transitions=self.transitions,
		# 							 initial=ras.TURN_STARTED)
		# 	def next(self):
		# 		getattr(self, ras.Triggers.NEXT)()

		def __init__(self,ros_node_mgr,task_controller):
			
			self.states = [ ris.ROBOT_TURN, ris.CHILD_TURN ]
			self.transitions = [
				{'trigger': ris.Triggers.CHILD_TURN_DONE, 'source': ris.CHILD_TURN, 'dest': ris.ROBOT_TURN },
				{'trigger': ris.Triggers.ROBOT_TURN_DONE, 'source': ris.ROBOT_TURN, 'dest': ris.CHILD_TURN},
			]

			self.state_machine = Machine(self, states=self.states, transitions=self.transitions,
									 initial=ris.CHILD_TURN)

			self.ros_node_mgr = ros_node_mgr

			self.task_controller = task_controller

			self.agent_model = AgentModel()

			self.role_behavior_mapping = RobotRolesBehaviorsMap()

			# robot's physical actions
			self.physical_actions ={}
			# robot's virtual actions on the tablet
			self.virtual_action = ""

			self.robot_response = self.role_behavior_mapping.get_actions("Response")

			

		def turn_taking(self):
			# check whether it is robot's turn or child's turn in the game play
			if self.state == ris.ROBOT_TURN:
				# then, next turn is child's 
				getattr(self, ris.Triggers.ROBOT_TURN_DONE)() # convert the variable to string, which is the name of the called function
		
			elif self.state == ris.CHILD_TURN:
				# then, next turn is robot's
				getattr(self, ris.Triggers.CHILD_TURN_DONE)()
	
			print("==========TURN TAKING===============: Current Turn = "+self.state)

			
			# robot's response 
			self.get_turn_taking_actions()

		
		def react(self,gameStateTrigger):
			'''
			react to ispy game state change
			'''
			if gameStateTrigger == gs.Triggers.TARGET_OBJECT_COLLECTED:
				if self.state == ris.ROBOT_TURN:
					# robot just collected an object. celebrate
					self._perform_robot_physical_action(self.physical_actions[ras.TURN_FINISHED])
				elif self.state == ris.CHILD_TURN:
					self._perform_robot_physical_action(self.robot_response["physical"][ras.TURN_FINISHED])
			

			elif gameStateTrigger  == gs.Triggers.OBJECT_CLICKED:
				if self.state == ris.ROBOT_TURN:
					#robot's turn, pronounce the word
					self._perform_robot_physical_action(self.physical_actions[ras.OBJECT_CLICKED])
				elif self.state == ris.CHILD_TURN:
					self._perform_robot_physical_action(self.robot_response["physical"][ras.OBJECT_CLICKED])
			
			
			elif gameStateTrigger  == gs.Triggers.SAY_BUTTON_PRESSED:
				if self.state == ris.ROBOT_TURN:
					self._perform_robot_physical_action(self.physical_actions[ras.OBJECT_PRONOUNCED])

			
			elif gameStateTrigger  == gs.Triggers.PRONUNCIATION_PANEL_CLOSED:
				if self.state == ris.CHILD_TURN:
					self._perform_robot_physical_action(self.robot_response["physical"][ras.WRONG_OBJECT_FAIL])

			elif gameStateTrigger == gs.Triggers.TOPLEFT_BUTTON_PRESSED:
				pass
				#self.interaction.send_robot_action(RobotBehaviors.REACT_GAME_START)
				#self.interaction.send_robot_action(RobotBehaviors.REACT_GAME_START2)
				
					

		def get_turn_taking_actions(self):
			'''
			check the current interaction FSM to decide whether the robot should respond
			then, use agent model to decide how the robot should respond if it needs to respond
			'''

			physical_actions = {}
			virtual_action = ""

			if self.state == ris.ROBOT_TURN:
				# choose an action for robot
				print("Turn Taking Action...ROBOTS TURN")
		
				actions = self._get_behaviors()
				physical_actions = actions['physical'] 
				virtual_action = actions['virtual']

			elif self.state == ris.CHILD_TURN:
				# no need to respond at this point 
				print("Turn Taking Action...CHILD TURN")

			if physical_actions:
				self.physical_actions = physical_actions
				self._perform_robot_physical_action(self.physical_actions[ras.TURN_STARTED])
			if virtual_action:
				time.sleep(1) 
				self._perform_robot_virtual_action(virtual_action)



		def _get_behaviors(self):
			'''
			Get corresponding virtual and physical actions for a given input robot's role
			'''
			role = self.agent_model.get_next_robot_role()
			return self.role_behavior_mapping.get_actions(role)
			

		def _perform_robot_physical_action(self,actions):
			'''
			send the physical action message via ROS to the robot
			'''

			print("perform robot physical action runs..")
			for action in actions:
				# if the action is to pronounce a word, then specify a word to pronounce
				if action == RobotBehaviors.PRONOUNCE_CORRECT:
					if not self.robot_clickedObj:
						self.robot_clickedObj = "cat"
					self.ros_node_mgr.send_robot_cmd(action,self.robot_clickedObj)
				else:
					self.ros_node_mgr.send_robot_cmd(action)
				time.sleep(1)

		def _perform_robot_virtual_action(self,action):
			'''
			send the virtual action message via ROS to the tablet 
			'''
			print("perform robot virtual action")
			print(action)
			self.robot_clickedObj = self.get_game_object_for_clicking()

			self.ros_node_mgr.send_ispy_cmd(iSpyCommand.ROBOT_VIRTUAL_ACTIONS,{"robot_action":action,"clicked_object":self.robot_clickedObj})
			


		def get_game_object_for_clicking(self):
			'''
			get game obejct for the robot to click during robot's turn
			'''
			return self.task_controller.get_obj_for_robot(True)