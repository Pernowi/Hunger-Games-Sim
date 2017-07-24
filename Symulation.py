import PlayerClass
import ActionMethods
import Log
import Items
import copy
import random

class Sym:
	# logName - string
	def __init__(self,logName):
		self.listOfTeams = []	# Team - a list of players with some additional stuff.
		self.dayDuration = 12	# Amount of hours in a day
		self.hourlyCalorieCost = 50 # calorie cost per hour - no matter the action
		self.theLog = Log.LogObject(logName)	# log where stuff is going to be written. For now only for testing purposes.
	# runs symulation for one day
	def runForADay(self):
		for t in self.listOfTeams:
			t.resetPlayersTime()
			
		stringToWrite = "---Status:\n"
		for team in self.listOfTeams:
			for p in team.playerList:
				stringToWrite+=p.getStringStatus(1)+ "\tinventory\n"+ p.getStringItemList(2)
		self.theLog.writeToLog(stringToWrite)
		allFinished = False
		while not allFinished:
			random.shuffle(self.listOfTeams) # this shuffle is so that one team doesn't always go first
			result = self.findEarlyiestPlayer()
			# To implement - teams make actions as a group. Sometimes only part of the team does the action.
			if result[0] is None:
				allFinished = self.areAllFinished()
				break
			playersPerformingAction = result[1].listOfPlayersWithGivenTime(result[0].simTime)
			resultOfDecision = self.makeGroupDecisionNoCathegories(playersPerformingAction)
			action = resultOfDecision[0]
			target = resultOfDecision[1]
			ideaOriginators = resultOfDecision[2]
			resultOfRebelDetection = self.detectRebelsAndRemoveThemFromParticipants(playersPerformingAction,ideaOriginators)
			listOfRebels = resultOfRebelDetection[0]
			playersPerformingAction = resultOfRebelDetection[1]
			# now we have to implement bumps. For now takeCareOfBumo doesn't work, since I need to implement relationships first
			bumpDidntFailAction = self.takeCareOfBump(playersPerformingAction,target)
			if bumpDidntFailAction:
				actionResult = action.applyAction(playersPerformingAction,target)
			else:
				actionResult = action.failAction(playersPerformingAction,target)
					
			# This listOfPerformers is only for log to look nice. Players that are target and performer are removed from performers lists by action methods anyway to be extra safe.
			if not target is None:
				listOfPerformers = [x for x in playersPerformingAction if x not in target]
			else:
				listOfPerformers = playersPerformingAction
			
			self.writeActionInformationToLog(action,actionResult,listOfPerformers,target,listOfRebels,ideaOriginators)
			
			for p in playersPerformingAction:
				p.removeCalories(self.hourlyCalorieCost*action.time)
				p.simTime+=action.time		
				p.passTimeOnAfflictions(action.time)
				afflictionChanges = p.checkForAfflictionsToPutAndRemove()
				#print(afflictionChanges)
				self.writeAfflictionInformationToLog(p,afflictionChanges)
						
				stringToWrite = p.getStringStatus(1) + "\tinventory\n"+ p.getStringItemList(2) + "\ttime passed so far:{}\n".format(p.simTime)
				self.theLog.writeToLog(stringToWrite) # Writes player status to the log
				isDead = p.isDead()
				if isDead[0]:
					result[1].removePlayer(p.id)
					stringToWrite=p.Name+" "+isDead[1]+'\n'
					self.theLog.writeToLog(stringToWrite)
							
			allFinished = self.areAllFinished()
			
			
	# finds a player that has the least of time passed	
	# returns None if everyone is above dayDuration time
	def findEarlyiestPlayer(self):
		playerToReturn = None
		teamToReturn = None
		playerTime = self.dayDuration
		for team in self.listOfTeams:
			for player in team.playerList:
				if player.simTime<playerTime:
					playerTime = player.simTime
					playerToReturn = player
					teamToReturn = team
		return playerToReturn,teamToReturn # player with the least time passed - and his team
	# makes decision of one player
	# player - PlayerClass.Player
	# group - list of players, where decision making takes place. Player should be inside it.
	def makeDecisionNoCathegories(self,player,group):
		group.remove(player)
		group.insert(0,player)
		actionToReturn = None	# action to perform
		actionPlayers = None	# performers of the action
		actionTarget = None		# target of the action
		rebelReason = player.isRebel()
		if rebelReason == PlayerClass.Player.rebelReasonDict["hunger"]:
			result = ActionMethods.EatFoodCheck([player])
			if result:
				actionToReturn = PlayerClass.getActionByName("eat food")
				actionPlayers = [player]
			elif ActionMethods.AskForFoodCheck(group,[player]):
				actionToReturn = PlayerClass.getActionByName("ask for food")
				actionPlayers = group
				actionTarget = [player]
			else:
				actionToReturn = PlayerClass.getActionByName("gather food")
				actionPlayers = group
		else:
			# random action
			actionToReturn = PlayerClass.getPurelyRandomAction()
			actionPlayers = group
			if actionToReturn.name == "ask for food":
				actionTarget = [player]
		return actionToReturn, actionPlayers ,actionTarget
	
	# makes decision of group of players.
	# listOfPlayers - list with Player as elements
	def makeGroupDecisionNoCathegories(self,listOfPlayers):
		actionsAndPersuasionList = []
		action = None
		actionTarget = None
		for p in listOfPlayers:
			result = self.makeDecisionNoCathegories(p,listOfPlayers) # [0] - action, [1] - players performing action,[2] - players to perform action on
			action = result[0]
			actionPlayers = result[1]
			actionTarget = result[2]
			persuasion = p.Charisma + 0.4 * p.Intelligence + 0.1*random.randint(0,20)
			appendIsNeeded = True
			for AaP in actionsAndPersuasionList:
				if AaP[0].name == action.name:
					appendIsNeeded = False
					AaP[1]+=persuasion
					AaP[3].append(p)
					break
			if appendIsNeeded:
				actionsAndPersuasionList.append([action,persuasion,actionTarget,[p]])
		# find action with the biggest persuasion
		action = None
		actionTarget = None
		persuasion = -1
		for AaP in actionsAndPersuasionList:
			if AaP[1]> persuasion:
				persuasion = AaP[1]
				action = AaP[0]
				actionTarget = AaP[2]
				originators =AaP[3]
		return action,actionTarget,originators

	#detects if all players in all teams have finished actions for today	
	def areAllFinished(self):
		for team in self.listOfTeams:
			if not team.checkAllPlayersFinished(self.dayDuration):
				return False
		return True
			
	# Writes information about performed action into the log
	def writeActionInformationToLog(self,action,actionResult,playerList,targetList = None,listOfRebels = None,originators = None ):
		if actionResult:
			textToPrint = "success"
		else:
			textToPrint = "failure"
		playerNames = ""
		for p in playerList:
			playerNames+=p.Name+', '
		playerNames = playerNames[:-2]
		targetNames =""
		if (not targetList is None):
			if targetList:
				if not targetList[0] is None:
					targetNames = " targets: "
					for t in targetList:
						targetNames+=t.Name+', '
				targetNames = targetNames[:-2]
			
		rebelString = ""
		if (not listOfRebels is None):
			if listOfRebels:
				rebelString = "\n== People who rebelled: "
				for r in listOfRebels:
					# my god I goofed out. Dictionary in python is not meant to be used backwards
					# and so I ended up with this monstrosity. Oh well.
					tmpString = list(PlayerClass.Player.rebelReasonDict.keys())[list(PlayerClass.Player.rebelReasonDict.values()).index(r["cause"])]
					rebelString+="{0} for {1}, ".format(r["rebel"].Name,tmpString)
				rebelString = rebelString[:-2]
		originatorsText = ""
		if (not originators is None):
			if originators:
				originatorsText = " originators:"
				for o in originators:
					originatorsText+=o.Name+', '
				originatorsText = originatorsText[:-2]
		stringToWriteToLog = "\n==== Action Performed: {0}, result:{1}\n== Action performed by:{2}".format(action.name,textToPrint,playerNames)
		stringToWriteToLog+=targetNames+originatorsText+rebelString+'\n'
		self.theLog.writeToLog(stringToWriteToLog)
	
	# Writes information about gained and lost afflictions
	def writeAfflictionInformationToLog(self,player,afflictionChanges):
		afflictionStringToWrite = ""
		if afflictionChanges[0]:	# added afflictions
			if len(afflictionChanges[0]) == 1:
				afflictionStringToWrite+="\t{} gained affliction: ".format(player.Name)
			else:
				afflictionStringToWrite+="\t{} gained afflictions: ".format(player.Name)		
			for a in afflictionChanges[0]:
				afflictionStringToWrite+="{}, ".format(a.name)
			afflictionStringToWrite = afflictionStringToWrite[:-2]
			afflictionStringToWrite+='\n'
		if afflictionChanges[1]:	# removed afflictions
			if len(afflictionChanges[1]) == 1:
				afflictionStringToWrite+="\t{} lost affliction: ".format(player.Name)
			else:
				afflictionStringToWrite+="\t{} lost afflictions: ".format(player.Name)		
			for a in afflictionChanges[1]:
				afflictionStringToWrite+="{}, ".format(a.name)
			afflictionStringToWrite = afflictionStringToWrite[:-2]
			afflictionStringToWrite+='\n'
		if not afflictionStringToWrite == "":
			self.theLog.writeToLog(afflictionStringToWrite)
	
	# gives all players an unique id - becuase things go bad if they are not unique.
	def giveAllPlayersUniqueIDs(self):
		listOfUsedIDs = []
		id = 0
		for team in self.listOfTeams:
			for player in team.playerList:
				while id in listOfUsedIDs:
					id = random.randint(1,100000)
				player.id = id
				listOfUsedIDs.append(id)

	# of course, targets have no say in if they want to be a part of an action or not.
	# returns a list of rebels
	def detectRebelsAndRemoveThemFromParticipants(self, listOfPlayers, ideaOriginators):
		listOfRebels = []
		listOfParticipants = []
		rebelReason = None
		for player in listOfPlayers:
			rebelReason = player.isRebel()
			if rebelReason != PlayerClass.Player.rebelReasonDict["no rebel"] and not player in ideaOriginators:
				listOfRebels.append({"rebel":player,"cause":copy.deepcopy(rebelReason)})
			else:
				listOfParticipants.append(player)
		return listOfRebels,listOfParticipants

	# Well. This method takes care of bumps
	# If there was no bump, or bump didn't interrupted current action
	def takeCareOfBump(self, listOfPlayers,target):
		listOfBumpablePlayers = []
		return True
class Team:
	# listOfPlayers - list with players as elements
	def __init__(self,listOfPlayers):
		self.playerList = listOfPlayers
		self.allPlayersFinished = False
	# returns a player from list. None, if player is not in team.
	# name - either string or int
	def getPlayer(self,name):
		if type(name) is int:
			for p in self.playerList:
				if p.id == name:
					return p
		elif type(name) is str:
			for p in self.playerList:
				if p.Name == name:
					return p
		else:
			raise Exception("Wrong parameter type")
		return None
	# checks if all players have finished the day.
	# dayTimeLimit - int
	def checkAllPlayersFinished(self,dayTimeLimit):
		for p in self.playerList:
			if p.simTime<dayTimeLimit:
				self.allPlayersFinished = False
		self.allPlayersFinished = True
	# sets all players time in the team to zero
	def resetPlayersTime(self):
		for p in self.playerList:
			p.simTime = 0
	# checks, if all players have the same time.
	# players with different times can't perform an action together.
	# becasue they are in different points in time
	def areAllPlayersTheSameTime(self):
		time = self.playerList[0].simTime
		for p in self.playerList:
			if not p.simTime == time:
				return False
		return True
	# Returns list of players with the same time	
	def listOfPlayersWithGivenTime(self,time):
		listToReturn = []
		for p in self.playerList:
			if p.simTime == time:
				listToReturn.append(p)
		return listToReturn
				
	# removes player from team. Returns true if player was removed.
	# name - str or int
	def removePlayer(self,name):
		for p in self.playerList:
			if p.Name == name or p.id == name:
				self.playerList.remove(p)
				return True
		return False

# --- test ---

pl = PlayerClass.Player(0)
pl.BaseWisdom = 5
pl.Name = "Jan Kowalski"
pl.calculateStartStatistics()
pl2 = PlayerClass.Player(0)
pl2.BaseWisdom = 0
pl2.Name = "Adam Nowak"
pl2.calculateStartStatistics()
team = Team([pl,pl2])
theLog = Log.LogObject('log1')
s = Sym('log1')
s.listOfTeams.append(team)
s.giveAllPlayersUniqueIDs()
for x in range(1,100):
	theLog.writeToLog("\n~~ DAY {}~~\n\n".format(x))
	s.runForADay()