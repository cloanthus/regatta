import random
import csv
from common import *


class Game:
    def __init__(self, mapPath):
        # self.viewers = []
        # self.umpire = []
        self.boats = []
        self.buoyCount = 0
        self.buoys = [self.Buoy(self, (i, i)) for i in range(4)]
        self.wind = 0
        self.mapPath = mapPath
        self.map = self.Map(mapPath)
        self.legs = 0
        self.dice = self.Dice(['P', 'S', 1, 2, 2, 3])



        # self.playOrder = random.choices(self.players)
        # self.currentPlayer = 0   # index of current player

    def create_boat(self, boatID, pos=(0, 0), tack='S', heading=0, colour=colours['black']):
        boat = self.Boat(self, boatID, pos, tack, heading, colour)
        self.boats.append(boat)
        return boat

    def create_buoy(self, pos=(0, 0), colour=colours['buoy'], visible=True):
        self.buoys.append(self.Buoy(pos, colour, visible))

    def find_in_flotilla(self, boatID):
        for boat in self.boats:
            if boat.boatID == boatID:
                return boat
        print("boat not found")

    def get_positions(self, obj):
        switchKey = {'boats': self.boats,
                     'buoys': self.buoys
                     }
        return [obj.pos for obj in switchKey[obj]]

    def wind_shift(self, shift):
        self.wind = (self.wind + shift) % 8
        # send update?

    # def end_turn(self):
    #     self.currentPlayer = (self.currentPlayer + 1) % len(self.flotilla)

    class Boat:
        def __init__(self, game, boatID, pos, tack, heading, colour):
            self.pos = pos
            self.currentTack = tack
            self.heading = heading
            self.colour = colour
            self.boatID = boatID
            self.game = game

            self.spinnaker = False
            self.puff = False
            self.puffCounter = 2
            self.legCounter = 0

        def tack(self):
            if self.currentTack == 'P':
                self.currentTack = 'S'
                self.heading = (self.game.wind + 1) % 8
            if self.currentTack == 'S':
                self.currentTack = 'P'
                self.heading = (self.game.wind - 1) % 8

        def turn(self, action):
            points = [i for i in range(8)]
            sailActions = ['tack', 'spin.', 'puff']
            gameActions = ['roll', 'end']

            if action in points:
                self.heading = action
                relWind = (action - self.game.wind) % 8
                extra = int(self.spinnaker) + int(self.puff)
                self.pos = tuple(map(lambda x, y: x + (point2sailing[relWind] + extra) * y, self.pos, point2vec[action]))
                self.puff = False
                self.legCounter += 1
            elif action in sailActions:
                if action == 'tack':
                    self.tack()
                    self.legCounter += 1
                elif action == 'spin.':
                    self.spinnaker = not self.spinnaker
                    self.legCounter += 1
                elif action == 'puff':
                    self.puff = True
                    self.puffCounter -= 1
            elif action in gameActions:
                if action == 'roll':
                    self.game.dice.roll()

        def get_attr(self):
            return [self.boatID, self.pos, self.heading, self.spinnaker, self.colour]

        def get_colour(self):
            return [self.boatID, self.colour]

        def get_valid_moves(self):
            if self.game.dice.outcome == 'P' or self.game.dice.outcome == 'S':
                return ['roll']
            elif self.legCounter <= 100 and not self.blanketed():  # !game.legs
                validMoves = ['spin.', 'tack']
                if self.puffCounter > 0:
                    validMoves.append('puff')
                switchTacks = {'P': [i for i in range(1, 5)],
                               'S': [i for i in range(4, 8)]
                               }
                switchSpinn = {True: [3, 4, 5],
                               False: [i for i in range(8)]}
                sailablePoints = list(set(switchTacks[self.currentTack]) & set(switchSpinn[self.spinnaker]))
                for point in range(8):
                    relWind = (point - self.game.wind) % 8
                    if relWind in sailablePoints:
                        extra = int(self.spinnaker) + int(self.spinnaker)
                        path = [tuple(map(lambda x, y: x + i*y, self.pos, point2vec[point])) for i in range(1, point2sailing[relWind] + extra + 1)]
                        validPath = []
                        for pos in path:
                            try:
                                occupied = (pos in self.game.get_positions('boats')) or pos in self.game.get_positions('buoys')
                                offBoard = any([pos[i] < 0 for i in range(len(pos))])
                                validPath.append(all([self.game.map.is_clear(pos), not occupied, not offBoard]))
                            except:
                                print('ERROR HERE')
                        if all(validPath):
                            validMoves.append(point)
                if self.currentTack == 'P':
                    validMoves.append('S')
                elif self.currentTack == 'S':
                    validMoves.append('P')
                return validMoves
            else:
                return ['end turn']

        def blanketed(self):
            upwind = [tuple(map(lambda x, y: x + i*y, self.pos, point2vec[self.game.wind])) for i in range(1,3)]
            for boat in self.game.boats:
                if boat.pos == upwind[0]:
                    return True
                if boat.pos == upwind[1] and boat.spinnaker:
                    return True
            return False

    ###############################################################################################
    class Buoy:
        def __init__(self, game, pos, visible=True):
            self.pos = pos
            self.isFinish = False
            self.buoyID = game.buoyCount
            game.buoyCount += 1
            self.game = game
            # self.visible = visible

        def get_attr(self):
            return [self.buoyID, self.pos, self.isFinish]

        def move(self, point):
            newPos = tuple(map(lambda x, y: x + y, self.pos,  point2vec(point)))
            if all([i >= 0 for i in newPos]):
                self.pos = newPos

    ###############################################################################################
    class Dice:
        def __init__(self, faces):
            self.faces = faces
            self.outcome = random.choices(self.faces)[0]

        def roll(self):
            self.outcome = random.choices(self.faces)[0]
            # if type(self.outcome) is int:
            #     self.legs = self.outcome  # can't see the game from here
            return self.outcome

    ###############################################################################################
    class Map:
        def __init__(self, file):
            terrainKey = {'0': 'sea',
                          '1': 'land',
                          '2': 'buoy'
                          }
            with open(file, newline='') as f:
                reader = csv.reader(f)
                terrainFile = list(reader)
            self.size = (len(terrainFile[0]), len(terrainFile))
            self.terrain = []
            for x in range(self.size[0]):  # ! using list comprehension would be nicer
                self.terrain.append([])
                for y in range(self.size[1]):
                    self.terrain[x].append([terrainKey[terrainFile[y][x]]])

        def get_square(self, pos):
            return self.terrain[pos[0]][pos[1]]

        def is_clear(self, pos):
            if self.get_square(pos)[0] == 'sea':
                return True
            else:
                return False
