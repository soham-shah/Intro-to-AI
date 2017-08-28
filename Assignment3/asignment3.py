#Name: Soham Shah
#Class: Intro to AI
#Instructor: Rhonda Hoenigman
#Assignment 3
#the goal of this is to create a graph from a text file and run a* search on it.

import sys
import heapq
import time

class Graph:
    def __init__(self):
        self.vertices = {}
        self.heuristic = {}

    def addVertex(self, value):
        # check if value already exists
        if value in self.vertices:
            print
            "Vertex already exists"
        else:
            self.vertices[value] = {}

    def addHeuristic(self,node, value):
        self.heuristic[node] = value

    def addEdge(self, value1, value2, weight):
        if (value1 in self.vertices and value2 in self.vertices):
            self.vertices[value1][value2]= weight
            self.vertices[value2][value1]= weight
        else:
            print("One or more vertices not found.")

    def printGraph(self):
        print(self.vertices)

    def printHeuristic(self):
        print(self.heuristic)

    def dijsktra(self, initial, end):

        start = time.time()

        complexity = 0
        distances = {} #keep track of distance to each node
        previous = {} #keep track of shortest path to each node
        priorityQueue = [] #priority queue of things to check next

        for i in self.vertices:
            if i == initial:
                distances[i] = 0
                heapq.heappush(priorityQueue, [0, i]) #add i to priority queue with initial dist of 0
            else:
                distances[i] = sys.maxsize
                heapq.heappush(priorityQueue, [sys.maxsize, i])
            previous[i] = None
            complexity+=1

        while (priorityQueue):
            node = heapq.heappop(priorityQueue)[1]

            # if we've reached the end it's the most efficient and so get the path and break out.
            if node == end:
                path = []
                while previous[node]:
                    path.append(node)
                    node = previous[node]
                path.append(initial)
                path.reverse()
                return ({"Algorithm":"Dijkstra's", "Path":path, "Distance": distances[end], "Nodes Evaluated":complexity, "time taken": time.time()-start})

            #otherwise update the distances based on the time it takes to get to this node
            for adj in self.vertices[node]:
                complexity+=1
                alternatePath = distances[node] + self.vertices[node][adj]
                if alternatePath < distances[adj]:
                    distances[adj] = alternatePath
                    previous[adj] = node #update the path taken

                    #update the priority queue with the new distance info
                    for n in priorityQueue:
                        if n[1] == adj:
                            n[0] = alternatePath
                            break
                    heapq.heapify(priorityQueue)

    def aStar(self, start, goal):
        begining = time.time()

        complexity = 0
        priorityQueue = []
        parentNode = {}
        totalCost = {}

        parentNode[start] = None
        totalCost[start] = 0
        heapq.heappush(priorityQueue, [0, start])

        while priorityQueue:
            current = heapq.heappop(priorityQueue)[1] #get the closest node from the pq

            if current == goal: #if we've reached the end, then break out
                break
            for adj in self.vertices[current]: #add the new nodes in the list
                complexity+=1
                newCost = totalCost[current] + self.vertices[current][adj]
                if adj not in totalCost or newCost < totalCost[adj]:
                    totalCost[adj] = newCost
                    estimate = newCost + self.heuristic[adj]
                    heapq.heappush(priorityQueue, [estimate, adj])
                    parentNode[adj] = current

        #figure out the path based on the parent list
        path = []
        path.append(goal)
        node = parentNode[goal]
        while node!= start:
            path.append(node)
            node = parentNode[node]
        path.append(start)
        path.reverse()

        return ({"Algorithm":"A* Search", "Path": path, "Distance": totalCost[goal], "Nodes Evaluated": complexity, "time taken": time.time()-begining})


#begining of the main code outside the class
test = Graph()

#code for reading the text file and creating the graph
#Filename: "Assignment3.txt"
for line in open(sys.argv[1],"r"):
    #this means it's a weighted node in the graph so add it here
    if line[0]== "[":
        test.addVertex(line[1])
        test.addVertex(line[3])
        test.addEdge(line[1],line[3],int(line[5]))
    #If the line isn't just blank then it's a heuristic
    elif(line!="\n"):
        test.addHeuristic(line[0],int(line[2:len(line)]))

#test.printGraph()
#test.printHeuristic()

print(test.dijsktra("S","F"))
print(test.aStar("S","F"))
