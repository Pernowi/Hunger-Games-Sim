import ActionMethods
import Items
import Log
import copy
import random

class Player:
	rebelReasonDict = {"no rebel":0,"hunger":1,"stress":2,"health":3}
	def __init__(self, Id):
		self.id = Id
		#these are strings
		self.Name = ""
		#these are all ints
		self.BaseStrength = 0			# Represents ability of how hard your character can hit things.
		self.BaseAgility = 0			# Represents skill in tasks that require precision and balance.
		self.BaseEndurance = 0			# Represents resistance to damage and sickness. More fat supply at the start (200 per point). 
		self.BaseIntelligence = 0		# Represents ability to solve complex problems, as well as tactical thinking.
		self.BaseWisdom = 0				# Represents knowledge about the world, and ability to use it.
		self.BaseCharisma = 0			# Represents ability to manipulate and appeal to people. Increases chance of getting something from a sponsor.

		self.Strength = 0			# Represents ability of how hard your character can hit things.
		self.Agility = 0			# Represents skill in tasks that require precision and balance.
		self.Endurance = 0			# Represents resistance to damage and sickness. More fat supply at the start (200 per point). 
		self.Intelligence = 0		# Represents ability to solve complex problems, as well as tactical thinking.
		self.Wisdom = 0				# Represents knowledge about the world, and ability to use it.
		self.Charisma = 0			# Represents ability to manipulate and appeal to people. Increases chance of getting something from a sponsor.
		#list of perks
		self.perks = []				# Perks choosen by the player.
		#list of relationships
		self.relationships = []		# Represents relationships character has with other tributes.
		#list of afflictions
		self.afflictions = []		# Represents temporary or not things that are affecting character.
		#list of items
		self.itemList = []			# List of items posessed by tribute
		
		#these are floats
		self.CaloriePool = 0	#Max amount of calories. If you have more, it gets transformed into Fat.
		self.Fat = 0			#Amount of Fat your character has. All characters start with 4000.0+200*Endurance calories of Fat. At 10000 calories you get "obese" penalty. At 500 you get "starving" penalty.
		self.Calories = 0		#Amount of non-fat calories that character can utilise. If this number reaches 0, character begins burning Fat reserves and gets "ketosis" penalty.
		self.Stress = 0			#Stress accumulates over time. Some events cause more stress than others. If characters stress is high enough, it will perform actions aimed at reducing it. Stress can't be lesser than zero. If stress reaches 100, character will go insane.
		self.HealthPoints = 0	#Amount of HealthPoints your character has. 0 means death.
		self.MaxHealthPoints = 0 #Maximum amount of HealthPoints your character can have.
	
		#this is int
		self.simTime =0
	def putAffliction(self,affliction):
		self.afflictions.append(affliction)
	def removeAffliction(self,affliction):
		for a in self.afflictions:
			if a.name == affliction.name:
				self.afflictions.remove(a)
	def addItem(self,item):
		self.itemList.append(copy.deepcopy(item))
	def removeItem(self,item):
		for i in self.itemList:
			if i.nameValue[0] == item.nameValue[0]:
				self.itemList.remove(i)
				break
	def findItemWithOneOfItemFunctions(self,ListOfItemFunctions):
		for i in self.itemList:
			for itemFunction in ListOfItemFunctions:
				if i.function.id == itemFunction.id:
					return True, i
		return False, None
	def findListOfItemsWithOneOfItemFunctions(self,ListOfItemFunctions):
		listOfItems = []
		for i in self.itemList:
			hasFunction = False
			for itemFunction in ListOfItemFunctions:
				if i.function.id == itemFunction.id and i not in listOfItems:
					listOfItems.append(i)
					
		return listOfItems
	def computePerksCost(self):
		sum = 5
		for p in self.perks:
			sum-=p.cost
		return sum
	def recalculateStatistics(self):
		self.CaloriePool = 0	#Max amount of calories. If you have more, it gets transformed into Fat.
		self.MaxHealthPoints = 0 #Maximum amount of HealthPoints your character can have.

		self.Strength=self.BaseStrength
		self.Agility=self.BaseAgility
		self.Endurance=self.BaseEndurance
		self.Wisdom=self.BaseWisdom
		self.Intelligence=self.BaseIntelligence
		self.Charisma=self.BaseCharisma
		
		for p in self.perks:
			if(p.id == 0):
				self.Strength=self.Strength-2
				self.Agility=Agility-2
				self.Endurance=self.Endurance-2
				self.Fat+=10000.0
			elif(p.id == 1):
				self.Strength-=1
				self.Agility-=1
				self.Endurance-=1
				self.Intelligence-=1
				self.Wisdom-=1
				self.Charisma-=1
			elif(p.id == 2):
				self.Strength+=1
				self.Agility+=1
				self.Endurance+=1
				self.Intelligence+=1
				self.Wisdom+=1
				self.Charisma+=1
			elif(p.id == 3):
				self.Charisma+=2
			elif(p.id == 5):
				self.Endurance-=1
				self.Intelligence+=1
				self.Wisdom+=1
				self.Charisma+=1
			elif(p.id == 7):
				self.Wisdom+=1
			elif(p.id == 8):
				self.Wisdom+=2
		for a in self.afflictions:
			self.Strength+=a.dStrength
			self.Agility+=a.dAgility
			self.Endurance+=a.dEndurance
			self.Wisdom+=a.dWisdom
			self.Intelligence+=a.dIntelligence
			self.Charisma+=a.dCharisma		
			self.CaloriePool +=a.dCaloriePool
			self.MaxHealthPoints +=a.dMaxHealthPoints
			
			self.Fat +=a.dFat
			self.Calories +=a.dCalories
			self.Stress+=a.dStress
			self.HealthPoints+=a.dHealthPoints
		
		self.CaloriePool += 1000.0+100*self.Endurance
		self.MaxHealthPoints += 10 + 2*self.Endurance + 1*self.Strength
	def calculateStartStatistics(self):
		self.CaloriePool = 0	#Max amount of calories. If you have more, it gets transformed into Fat.
		self.Fat = 0			#Amount of Fat your character has. Amount of fat can increase if your characters eats something containing fat. All characters start with 4000.0+200*Endurance calories of Fat. At 10000 calories you get "obese" penalty. At 500 you get "starving" penalty.
		self.Calories = 0		#Amount of non-fat calories that character can utilise. If this number reaches 0, character begins burning Fat reserves and gets "ketosis" penalty.
		self.Stress = 0			#Stress accumulates over time. Some events cause more stress than others. If characters stress is high enough, it will perform actions aimed at reducing it. Stress can't be lesser than zero. If stress reaches 100, character will go insane.
		self.HealthPoints = 0	#Amount of HealthPoints your character has. 0 means death.
		self.MaxHealthPoints = 0 #Maximum amount of HealthPoints your character can have.
		self.recalculateStatistics()
		self.Fat += 4000.0+200*self.Endurance
		self.Calories += self.CaloriePool
		self.Stress += 0
		self.HealthPoints += self.MaxHealthPoints
	def addCalories(self,amount):
		self.Calories+=amount
		if self.Calories>self.CaloriePool:
			self.Fat+=(self.Calories-self.CaloriePool)
			self.Calories = self.CaloriePool
		if self.Calories<0:
			self.Fat+=self.Calories
			self.Calories = 0
	def removeCalories(self,amount):
		self.addCalories(-amount)
	def getStringStatus(self,offset = 0):
		stringToPrint = ""
		stringToPrint+="\t"*offset+"name: {}\n".format(self.Name)
		stringToPrint+="\t"*(offset+1)+"Calories: {}\n".format(self.Calories)
		stringToPrint+="\t"*(offset+1)+"Fat: {}\n".format(self.Fat)
		stringToPrint+="\t"*(offset+1)+"HealthPoints: {}\n".format(self.HealthPoints)
		stringToPrint+="\t"*(offset+1)+"Stress: {}\n".format(self.Stress)
		return stringToPrint
	def getStringItemList(self,offset = 0):
		stringToPrint = ""
		for it in self.itemList:
			stringToPrint+="\t"*(offset)+it.__str__()+'\n'
		if not self.itemList:
			return "\t"*(offset)+"*empty*\n"
		return stringToPrint
	def isDead(self):
		if self.Fat < 0:
			return True, "starved to death"
		elif self.HealthPoints <0:
			return True, "died of body system failure"
		return False, "is alive"
	def isRebel(self):
		if self.Calories < 200 or self.Fat < 1000:
			return self.rebelReasonDict["hunger"]
		return self.rebelReasonDict["no rebel"]
		
class Perk:
	def __init__(self,Cost,Id,Name,Description):
		# intigers
		self.cost = Cost
		self.id = Id
		# string
		self.name = Name
		self.description = Description

class Relationship:
	def __init__(self,Id):
		self.id = Id	# Character towards with which relationship is.
		self.value = 0	# Value of that relationship. Positive is good, negative is bad, 0 is neutral.
	def changeValue(self,change):
		self.value+=change
		
class Affliction:
	def __init__(self,Name,Time,Description,dStrength,dAgility,dEndurance,dIntelligence,dWisdom,dCharisma,dCaloriePool,dFat,dCalories,dStress,dMaxHealthPoints, dHealthPoints):
		self.name = Name
		self.time = Time
		self.description = Description
		
		self.dStrength = dStrength
		self.dAgility = dAgility
		self.dEndurance = dEndurance
		self.dIntelligence = dIntelligence
		self.dWisdom = dWisdom
		self.dCharisma = dCharisma
		
		self.dCaloriePool = dCaloriePool
		self.dFat = dFat
		self.dCalories = dCalories
		self.dStress = dStress
		self.dMaxHealthPoints = dMaxHealthPoints
		self.dHealthPoints = dHealthPoints

class Action:
	def __init__(self,Name,Cathegory,DescriptionList,CheckFunction,SuccessEffectFunction,FailureEffectFunction,Time = 1):
		self.name = Name
		self.descriptionList = DescriptionList
		self.successEffectFunction = SuccessEffectFunction
		self.failureEffectFunction = FailureEffectFunction
		self.checkFunction = CheckFunction
		self.time = Time 	#time in hours
	def applyAction(self,PlayerList,TargetsList=None):
		# let check, success and failure function have starargs *.
		# First one is PlayerList of players that perform the action
		# Second one are players affected by that action
		if self.checkFunction(PlayerList,TargetsList):
			self.successEffectFunction(PlayerList,TargetsList)
			return True
		else:
			self.failureEffectFunction(PlayerList,TargetsList)
			return False
		
listOfAllPerks = []
listOfAllPerks.append(Perk(-1,0,"Fat","Your character is FAT. It adds 10000.0 Calories to your supply of fat, and you suffer -2 to your all Body Attributes"))
listOfAllPerks.append(Perk(-4,1,"Belov Average","All your attributes suffer -1 penalty"))
listOfAllPerks.append(Perk(4,2,"Above Average","All your attribtes gain +1 points"))
listOfAllPerks.append(Perk(2,3,"Attractive","Your Character makes others hearts pump faster. +2 to Charisma, positive bonus to relationships."))
listOfAllPerks.append(Perk(-6,4,"Blind","Your character is blind as a bat. Automatically fail in situations that require sight. No darkness penalties related to sight."))
listOfAllPerks.append(Perk(2,5,"Educated","Your character is well educated in standard useless in wilderness stuff like math or history. +1 to Intelligence, Wisdom and Charisma, -1 to Endurance."))
listOfAllPerks.append(Perk(1,6,"Monk","Enables meditation as an efficient form of relieving stress."))
listOfAllPerks.append(Perk(1,7,"Wilderness Knowledge I","Your character knows basic things about surviving in the wild. +1 to Wisdom. More likely to pass checks that have something to do with surviving in the wild by small amount."))
listOfAllPerks.append(Perk(3,8,"Wilderness Knowledge II","Your character knows even more stuff about surviving in the wild. +2 to Wisdom. More likely to pass checks that have something to do with surviving in the wild by big amount."))
listOfAllPerks.append(Perk(2,9,"Fat Burning Machine","Your character gets no penalty when burning Fat. Only positives."))

listOfAllAfflictions = []
listOfAllAfflictions.append(Affliction("Hungry",-1,"Character is hungry. Adds stress. Increased chance of seeking food.",0,0,0,0,0,0,0,0,0,10,0,0))
listOfAllAfflictions.append(Affliction("Starving",-1,"Character is starving. Stress and body attribute penalty. Increased chance of seeking food.",-1,-1,-1,0,0,0,0,0,0,10,-5,0))
listOfAllAfflictions.append(Affliction("Obese",-1,"Character is obese. Body attribute penalty. Decreased chance of seeking food.",-1,-1,-1,0,0,0,0,0,0,0,0,0))
listOfAllAfflictions.append(Affliction("Dead",-1,"Nothing more to say. Character is dead.",0,0,0,0,0,0,0,0,0,0,0,0))


dictOfAllActions = {}
dictOfAllActions["gather food"] = Action("gather food","none",["party is gathering food"],ActionMethods.FoodSearchCheck,ActionMethods.FoodSearchSuccess,ActionMethods.FoodSearchFailure,2)
dictOfAllActions["eat food"] = Action("eat food","none",["party eats it's food"],ActionMethods.EatFoodCheck,ActionMethods.EatFoodSuccess,ActionMethods.Nothing,0)
dictOfAllActions["do nothing"] = Action("do nothing","none",["just do nothing"],ActionMethods.AlwaysTrueCheck,ActionMethods.Nothing,ActionMethods.Nothing,1)
dictOfAllActions["ask for food"] = Action("ask for food","none",["ask others in the group for food"],ActionMethods.AskForFoodCheck,ActionMethods.AskForFoodSuccess,ActionMethods.AskForFoodFailure,0)

def getActionByName(name):
	if name in dictOfAllActions:
		return dictOfAllActions[name]
	return None
	
def getPurelyRandomAction():
	return random.choice(list(dictOfAllActions.values()))
