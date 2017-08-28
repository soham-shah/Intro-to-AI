'''
Assignment: Assignment 5 Simulated Annealing
Class: CSCI 3202 Introduction to AI
Professor: Rhonda Hoenigman
Acknowledgements: Thanks to Scott Schubert for advice on how to approach to problem. 
Thanks to Mikhail Chowdhury for help on reading in the data and issues with probability
Used Professor Hoenigman's psuedocode for SA
'''

from random import randint
import sys
import math
import random
import copy

#reads in the data from the file and creates an array
def readInData():
	content = []
	for line in open(sys.argv[1]):

		# account for extra crap in largeState.txt
		line = line.replace(" \\", "")
		line = line.replace("\\", "")
		line = line.replace("}", "")
		line = line.replace("f0fs24cf0 ", "")

		# skip beginning lines in largeState.txt
		if ((line.strip()).startswith("D") or (line.strip()).startswith("R")):
			content.append(line.split())
	return content

#returns a dictionary of the popular vote
def getPopVote(content):
	results = {"D":0.0,"R":0.0}
	for i in content:
		for j in i:
			if (j == "D"):
				results["D"] += 1
			else:
				results["R"] += 1
	total = len(content)**2
	results["D"] = results["D"]/total*100
	results["R"] = results["R"]/total*100
	return results

#creates a district and returns as a dictionary
def generateInitialDistrict(number):
	districts = {}
	#initialize dictionary
	for i in range(0,number):
		districts[i] = []

	#place each node in place
	for i in range(0,number):
		for j in range (0,number):
			districts[i].append((i,j))
	return districts

#creates a new district that's similar to the previous district
def generateSimilarDistrict(number, district):
	#swap a small subset of nodes
	newDistrict = copy.deepcopy(district)
	createdAGoodArray = False
	while(createdAGoodArray != True):
		for i in range(0,2):
			#figure out which houses to swap
			randDistrict1 = randint(0,number-1)
			randHouse1 = randint(0,number-1)
			randDistrict2 = randint(0,number-1)
			randHouse2 = randint(0,number-1)

			#do the swap
			newDistrict[randDistrict1][randHouse1], newDistrict[randDistrict2][randHouse2] = newDistrict[randDistrict2][randHouse2], newDistrict[randDistrict1][randHouse1]
		createdAGoodArray = testDistrictValidity(newDistrict)
	#return the edited newDistrict
	return newDistrict

def testDistrictValidity(district):
	#create a set of potential contigious tuples based on whats in the set
	potentialContigious = []
	for i in district:
		for j in district[i]:
			#add all 4 possible nodes to the array
			potentialContigious.append((j[0]-1, j[1]))
			potentialContigious.append((j[0]+1, j[1]))
			potentialContigious.append((j[0], j[1]-1))
			potentialContigious.append((j[0], j[1]+1))

	for i in district:
		for j in district[i]:
			inPossible = False
			for k in potentialContigious:
				if j == k:
					inPossible = True
			if (inPossible == False):
				return False
	return True

#this function will calculate the how many districts each party wins
def countDistricts(houses, districts):
	results = {"D":0.0,"R":0.0}
	for i in districts:
		tempCount = {"D":0,"R":0}
		for j in districts[i]:
			if (houses[j[0]][j[1]] == "D"):
				tempCount["D"] += 1
			else:
				tempCount["R"] += 1
		if(tempCount["D"] > tempCount["R"]):
			results["D"] += 1
		else:
			results["R"] += 1
	return results

#This calculates how close a potential solution is to the popular vote
def getFitness(houses, districts, popVote):
	results = countDistricts(houses, districts)
	popVoteD = (popVote["D"])/((popVote["D"])+(popVote["R"]))
	resultsD = (results["D"])/((results["D"])+(results["R"]))
	return (abs(popVoteD- resultsD) / popVoteD)

def simulatedAnealing():
	houses = readInData()
	popVote = getPopVote(houses)
	districts1 = generateInitialDistrict(len(houses))
	
	T = sys.maxint #set the initial temperature
	Tmin = .000001 #minimum temp for the algorithm, tunable parameter
	alpha = 0.99 #temperature adjustment, tunable parameter

	numLoops = 1

	while (T > Tmin):
		districts2 = generateSimilarDistrict(len(houses), districts1)
		differenceInFitness=  getFitness(houses, districts2, popVote) - getFitness(houses, districts1, popVote)
		if (differenceInFitness < 0):
			#print "got a better one"
			districts1 = districts2
		else:
			exponent = differenceInFitness/(10000000*T)
			probability = math.exp(exponent)
			if(random.random < probability):
				#print "randomly broke the maxima"
				districts1 = districts2
		T = T* alpha
		numLoops +=1

	result = countDistricts(houses, districts1)
	return {"popVote": popVote, 
	"districts":districts1,
	"result":result,
	"NumLoops" : numLoops }

def printResults(results):
	print("Party division in population:")
	print("*"*37)
	print "R:<",results["popVote"]["R"],"%R>"
	print "D:<",results["popVote"]["D"],"%D>"
	print "*"*37
	print
	print "Number of districts with a majority for each party:"
	print "*"*37
	print "R: <",results["result"]["R"],">"
	print "D: <",results["result"]["D"],">"
	print "*"*37
	print "Locations assigned to each district:"

	for i in results["districts"]:
		print "District", i+1,
		for j in results["districts"][i]:
			print j,
		print

	print "*"*37
	print
	print "*"*37
	print "Algorithm applied : <SA>"
	print "*"*37
	print
	print "*"*37
	print "Number of search states explored: <", results["NumLoops"], ">"

printResults(simulatedAnealing())