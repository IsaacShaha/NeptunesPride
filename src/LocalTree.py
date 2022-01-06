### Edit this section.

#Get this from your game's url.
GAME_NUMBER = 5440848316334080
#Get this from settings in your game.
GAME_API = "sXbvMV"

### Libraries

import requests
import matplotlib.pyplot as plt
import networkx as nx
import math
import numpy as np
from operator import attrgetter

### Static Constants

INF = math.inf
GREEN = (0,1,0)
YELLOW = tuple(0.8*i for i in (1, 1, 0))
RED = (1,0,0)
BLACK = (0,0,0)
WHITE = (1,1,1)
GRAY = tuple(0.5*i for i in (1, 1, 1))
ORANGE = tuple(0.8*i for i in (1, 165/265, 0))
GRAY = (0.5, 0.5, 0.5)
WAR_STRATEGIES = {	"SWEEP":		0,
					"COMMUNISM":	1}
HOUR = 1/24

### Dynamic Constants

WAR_STRATEGY = WAR_STRATEGIES["SWEEP"]
NUM_CAPTURES = 3

### Classes

class Star:

	def __init__(self, name, x, y, playerId):
		self.name = name
		self.x = x
		self.y = y
		self.playerId = playerId
		self.isYours = Player.myPlayerId == playerId
		self.color = None
		self.capturePriority = INF

	def getDistance(self, otherStar):
		xDist = self.x - otherStar.x
		yDist = self.y - otherStar.y
		return (xDist**2 + yDist**2)**(1/2)

	def createEdge(self, otherStar):
		return Edge(self, otherStar, self.getDistance(otherStar))

	def setCapturePriority(self, capturePriority):
		self.capturePriority = capturePriority

	def belongsTo(self, player):
		return self.playerId == player.playerId

	def setColor(self, color):
		self.color = color

class Edge:
	def __init__(self, star1, star2, weight):
		self.star1 = star1
		self.star2 = star2
		self.weight = weight

class Player:

	def __init__(self, playerId, militaryPower, alias=''):
		self.playerId = playerId
		self.militaryPower = militaryPower
		self.alias = alias

	def getCenter(self, stars):
		xList = [star.x for star in stars]
		yList = [star.y for star in stars]
		xMean = sum(xList)/len(xList)
		yMean = sum(yList)/len(yList)
		return (xMean, yMean)

	def __str__(self):
		return f"Player {self.playerId} with military power {self.militaryPower}."

### Functions

def getDistance(pos1, pos2):
	xDist = pos1[0] - pos2[0]
	yDist = pos1[1] - pos2[1]
	return (xDist**2 + yDist**2)**(1/2)

def starColor(star):
	if star.isYours:
		if star.isFrontline:
			return YELLOW
		else:
			return GREEN
	else:
		if star.capturePriority <= NUM_CAPTURES:
			return RED
		else:
			return WHITE

def relevantNameFilter(star):
	if star.isYours or star.capturePriority <= NUM_CAPTURES:
		return star.name
	else:
		return ""

def generateGraph(stars, edges, display=True, save=False, showPlayerCenter=False):
	graph = nx.Graph()
	for star in stars:
		graph.add_node(	star.name, pos=(star.x, star.y),
						label=relevantNameFilter(star), color=star.color)
	for edge in edges:
		graph.add_edge(edge.star1.name, edge.star2.name)

	pos = nx.get_node_attributes(graph,'pos')
	labels = nx.get_node_attributes(graph, 'label')
	color = tuple(nx.get_node_attributes(graph, 'color').values())
	nx.draw(graph,
			pos,
			node_color=color,
			node_size=10,
			verticalalignment='bottom',
			width=0.5,
			edgecolors=BLACK,
			linewidths=0.5)
	labelPos = {}
	offset = 0.1
	for key in pos:
		labelPos[key] = (pos[key][0],pos[key][1]+offset)
	capturePos = {}
	captureLabels = {}
	for star in stars:
		if not star.isYours and star.capturePriority <= NUM_CAPTURES:
			capturePos[star.name] = (star.x, star.y)
			captureLabels[star.name] = star.capturePriority

	nx.draw_networkx_labels(graph,
							pos=labelPos,
							font_size=3,
							labels=labels)
	nx.draw_networkx_labels(graph,
							pos=capturePos,
							font_size=2,
							font_color=WHITE,
							font_weight='bold',
							labels=captureLabels)
	if display:
		plt.show()
	if save:
		plt.savefig("data/LatestMap.png", dpi=500)

### Data Collection

def getData(gameNumber, gameApi):
	api_url = "https://np.ironhelmet.com/api"
	params = {"game_number" : gameNumber,
					 "code" : gameApi,
			  "api_version" : "0.1"}
	payload = requests.post(api_url, params).json()
	players = payload["scanning_data"]["players"]

	myPlayerId = payload["scanning_data"]["player_uid"]
	Player.myPlayerId = myPlayerId
	stars = [payload["scanning_data"]["stars"][star] for star in payload["scanning_data"]["stars"]]
	starNodes = [Star(star['n'], float(star['x']), -float(star['y']), star["puid"]) for star in stars]
	myStars = [star for star in starNodes if star.isYours]
	for star in myStars:
		star.setColor(GREEN)
	otherStars = [star for star in starNodes if not star.isYours]
	for star in otherStars:
		star.setColor(WHITE)

	playersList = []
	for key in players:
		player = players[key]
		uid = player["uid"]
		shipCount = player["total_strength"]
		weaponsTech = player["tech"]["weapons"]["value"]
		militaryPower = shipCount*weaponsTech
		alias = player["alias"]
		if militaryPower == 0:
			continue
		playersList.append(Player(uid, militaryPower, alias))
		if uid == Player.myPlayerId:
			Player.myPlayer = playersList[-1]
	playersList.sort(key=attrgetter("militaryPower"), reverse=True)

	return {"starNodes":	starNodes,
			"myStars":		myStars,
			"otherStars":	otherStars,
			"myPlayerId":	myPlayerId,
			"players":		playersList}

def expandCapture(myStars, otherStars):

	capturePriority = [	star for star in otherStars
						if not star.belongsTo(Player.myPlayer)]
	xMean, yMean = Player.myPlayer.getCenter(myStars)
	capturePriority.sort(key=lambda star:
		getDistance((star.x, star.y), (xMean, yMean)))
	for i in range(NUM_CAPTURES):
		capturePriority[i].setCapturePriority(i+1)
		capturePriority[i].color = ORANGE
	nextCap = capturePriority[0]
	myClosestStar = myStars[0]
	for star in myStars:
		if star.getDistance(nextCap) < myClosestStar.getDistance(nextCap):
			myClosestStar = star
	myClosestStar.color = GRAY

def communistCapture(myStars, otherStars, players):

	enemies = [player for player in players if player != Player.myPlayer]
	enemies.sort(key=attrgetter("militaryPower"), reverse=True)
	enemy = enemies[0]
	capturePriority = [star for star in otherStars if star.belongsTo(enemy)]
	xMean, yMean = Player.myPlayer.getCenter(myStars)
	capturePriority.sort(key=lambda star:
		getDistance((star.x, star.y), (xMean, yMean)))
	for i in range(NUM_CAPTURES):
		capturePriority[i].setCapturePriority(i+1)
		capturePriority[i].color = RED
	nextCap = capturePriority[0]
	myClosestStar = myStars[0]
	for star in myStars:
		if star.getDistance(nextCap) < myClosestStar.getDistance(nextCap):
			myClosestStar = star
	myClosestStar.color = GRAY

def showMilitaryPower(players):
	militaryPowerList = sorted(players, key=attrgetter("militaryPower"), reverse=True)
	longestNameLength = sorted([len(player.alias) for player in players],
		reverse=True)[0]
	for i in range(len(militaryPowerList)):
		print(f"{i+1}: {militaryPowerList[i].alias:^{longestNameLength}} with a military power of " \
			f"{militaryPowerList[i].militaryPower}.")

def highlightStars(stars, myStars, otherStars, players):

	### Frontline Stars

	for enemyStar in otherStars:
		myClosestStar = None
		for myStar in myStars:
			if (myClosestStar == None or
				enemyStar.getDistance(myStar) < enemyStar.getDistance(myClosestStar)):
				myClosestStar = myStar
		myClosestStar.setColor(YELLOW)

	for myStar in myStars:
		alliedDistance = INF
		for alliedStar in myStars:
			if alliedStar == myStar:
				continue
			alliedDistance = min(alliedDistance, myStar.getDistance(alliedStar))
		enemyDistance = INF
		for enemyStar in otherStars:
			enemyDistance = min(enemyDistance, myStar.getDistance(enemyStar))
		if enemyDistance < alliedDistance*2:
			myStar.setColor(YELLOW)

	### Stars to Capture

	if WAR_STRATEGY == WAR_STRATEGIES["COMMUNISM"]:
	 	communistCapture(myStars, otherStars, players)
	elif WAR_STRATEGY == WAR_STRATEGIES["SWEEP"]:
		expandCapture(myStars, otherStars)
	showMilitaryPower(players)

def MST(stars):

	### Minimum Spanning Tree via Prim's Algorithm

	# number of vertices in graph
	V = len(stars)
	# create a 2d array of size 5x5
	# for adjacency matrix to represent graph
	G = []
	for i1 in range(V):
		star1 = stars[i1]
		G.append([])
		for i2 in range(V):
			star2 = stars[i2]
			G[-1].append(star1.getDistance(star2))
	# create a array to track selected vertex
	# selected will become true otherwise false
	selected = [0 for i in range(V)]
	# set number of edge to 0
	no_edge = 0
	# the number of edge in minimum spanning tree will be
	# always less than(V - 1), where V is number of vertices in
	# graph
	# choose 0th vertex and make it true
	selected[0] = True
	# print for edge and weight
	edges = []
	while (no_edge < V - 1):
		# For every vertex in the set S, find the all adjacent vertices
		#, calculate the distance from the vertex selected at step 1.
		# if the vertex is already in the set S, discard it otherwise
		# choose another vertex nearest to selected vertex  at step 1.
		minimum = INF
		x = 0
		y = 0
		for i in range(V):
			if selected[i]:
				for j in range(V):
					if ((not selected[j]) and G[i][j]):  
						# not in selected and there is an edge
						if minimum > G[i][j]:
							minimum = G[i][j]
							x = i
							y = j
		# print(str(x) + "-" + str(y) + ":" + str(G[x][y]))
		edges.append(stars[x].createEdge(stars[y]))
		selected[y] = True
		no_edge += 1
	return edges

def main():
	data = getData(GAME_NUMBER, GAME_API)
	stars = data["starNodes"]
	myStars = data["myStars"]
	otherStars = data["otherStars"]
	myPlayerId = data["myPlayerId"]
	players = data["players"]

	highlightStars(stars, myStars, otherStars, players)
	edges = MST(myStars)
	generateGraph(stars, edges, display=False, save=True)

if __name__ == "__main__":
	main()