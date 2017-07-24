import sys

#WARNING: ProgressBar uses /r to update itself. 
#Printing anything else to the console will cause the progress bar to wipe that written line instead of itself.

class ProgressBar:
	def __init__(self, maxdays, length = 25, initialday = 0):      #Only required argument is maxdays
		self.title = "Progress: "
		self.suffix = "({0}/{1} days)"
		self.lengthofbar = length              #Length of bar in characters
		self.day = initialday          #Progress determined by days completed out of maxdays (even if sim ends before maxdays)
		self.maxd = maxdays          
		self.write()

	def write(self):       #Write uses hash (#) as filled, dash (-) as empty
		value = (self.day*self.lengthofbar)/self.maxd
		barstring = '#'*value            
		emptystring = "-"*(self.lengthofbar-value)
		text = "\r{0}|{1}{2}|{3}".format(self.title, barstring, emptystring, self.suffix.format(self.day,self.maxd))
		sys.stdout.write(text)
		sys.stdout.flush()

	def changeToDay(self,day): #Use this to set the progress on the bar. Will automatically write to update itself.
		self.day = day
		self.write()

	def finish(self): #After simulation is over, this will start the next line on the terminal.
		sys.stdout.write("\n")
		sys.stdout.flush()
