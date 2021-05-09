import pygame
import numpy as np
from common import *
import csv
from network import Client
from _thread import *


# display settings
blockSize = 20
borderSize = 2


# # paired down boat class for drawing
class Boat:
    def __init__(self, attr):
        self.pos, self.heading, self.spinnaker, self.colour = attr

    def update(self, attr):     # attr = [pos, heading, spinnaker]
        self.pos, self.heading, self.spinnaker = attr

    def blankets(self, wind):
        if self.spinnaker:
            blanketRange = [1, 2]
        else:
            blanketRange = [1]
        return [tuple(map(lambda x, y: x - i*y, self.pos, point2vec[wind])) for i in blanketRange]


# paired down buoy class
class Buoy:
    def __init__(self, attr):
        self.pos, self.isFinish = attr

    def update(self, attr):
        self.pos, self.isFinish = attr


def draw_asset(asset, centre, scale=1.0, rotation=0.0, colour=colours['black'], lineWidth=0, boundingBox=None):
    def scale2fit(asset, boundingBox):
        assetSize = (max([vertex[0] for vertex in asset]) - min([vertex[0] for vertex in asset]),
                     max([vertex[1] for vertex in asset]) - min([vertex[1] for vertex in asset]))
        scales = (boundingBox[0] / assetSize[0], boundingBox[1] / assetSize[1])
        return min(scales)

    imgOut = []
    rotMatrix = np.array([[np.cos(rotation), -np.sin(rotation)],  # rotation matrix
                          [np.sin(rotation), np.cos(rotation)]])
    if boundingBox is not None:
        scale = scale2fit(asset, boundingBox)
    for vertex in asset:
        imgOut.append(np.add(rotMatrix.dot(vertex) * scale, centre))
    pygame.draw.polygon(window, colour, imgOut, width=lineWidth)


def create_map(file):
    with open(file, newline='') as f:
        reader = csv.reader(f)
        terra = list(map(lambda *x: list(x), *list(reader)))  # makes addressing [x][y]
    size = [len(terra), len(terra[0])]
    return size, terra


def coord2pixel(pos, corner='topLeft'):
    switch = {'topLeft': (pos[0] * (blockSize + borderSize) + borderSize, pos[1] * (blockSize + borderSize) + borderSize),
              'centre':  ((pos[0] + 0.5)*blockSize + (pos[0] + 1)*borderSize, (pos[1] + 0.5)*blockSize + (pos[1] + 1)*borderSize)
              }
    return switch[corner]


def point2radians(point):
    return point*(np.pi/4)


def draw_board():
    def draw_terrain(start=(0, 0), end=None):
        colourKey = {'0': colours['sea'],
                     '1': colours['land']}
        if end is None:
            end = boardSize
        for x in range(start[0], end[0]):
            for y in range(start[1], end[1]):
                rect = pygame.Rect(coord2pixel((x, y)), (blockSize, blockSize))
                pygame.draw.rect(window, colourKey[terrain[x][y]], rect)


    def draw_boats(flotilla):
        global wind
        # draw all blankets first to prevent overdrawing
        blankets = []                       # get all blankets
        for boat in flotilla.values():
            blankets += boat.blankets(wind)
        for pos in blankets:                # draw blankets
            if terrain[pos[0]][pos[1]] != '1':
                rect = pygame.Rect(coord2pixel(pos), (blockSize, blockSize))
                pygame.draw.rect(window, colours['blanketed'], rect)
        for boat in flotilla.values():      # draw boats
            draw_asset(assets['boat'], coord2pixel(boat.pos, 'centre'), rotation=point2radians(boat.heading), colour=boat.colour, boundingBox=[blockSize]*2)


    def draw_buoys(buoys):
        for buoy in buoys.values():
            if buoy.isFinish:     # if buoy is finish line
                colour = (255,255,255)
            else:
                colour = colours['buoy']
            draw_asset(assets['buoy'], coord2pixel(buoy.pos, 'centre'), boundingBox=[blockSize - 5]*2, colour=colour)

    draw_terrain()
    draw_boats(flotilla)
    draw_buoys(buoys)

def threaded_listen(connection):
    def upd_wind(data):     # data = windPoint
        global wind
        wind = data

    def upd_boat(data):     # data = [boatID, pos, heading, spinnaker, colour]
        global flotilla
        flotilla.update({data[0]: Boat(data[1:5])})

    # def upd_buoy(data):     # data = [buoyID, pos, isFinish]
    #     global buoyList
    #     buoyList.update()

    switch = {'wind': upd_wind,
              'boat': upd_boat,
              # 'buoy': upd_buoy
              }
    while run:
        update = connection.listen()    # update has form [property, value]
        if update is not None:
            switch[update[0]](update[1])
            print(update)
            draw_board()
    pass
    # listen for updates


########################################################
# make connection to server
n = Client()
clientID = n.connect('viewer')
# get initial game values
mapPath, boatList, buoyList, wind = n.send('get', 'initial')
# boats are received as [boatID, pos, heading, spinnaker, colour]
# buoys are received as [buoyID, pos, isFinish]
# create board
boardSize, terrain = create_map(mapPath)
# create flotilla
flotilla = {boat[0]: Boat(boat[1:5]) for boat in boatList}
buoys = {buoy[0]: Buoy(buoy[1:3]) for buoy in buoyList}

# initialise pygame window
pygame.init()
window = pygame.display.set_mode(tuple(i * (blockSize + borderSize) + borderSize for i in boardSize))
pygame.display.set_caption("boardViewer")
window.fill(colours['viewerBackground'])

################################
#         for testing          #
#
# buoys = {0: Buoy([(0, 6), False]),
#          1: Buoy([(10, 4), False]),
#          2: Buoy([(9, 3), True])
#          }
# flotilla = {0: Boat([(1, 20), 3, True, (0, 0, 0)]),
#             1: Boat([(5, 6), 1, True, (0, 100, 0)]),
#             2: Boat([(10, 10), 7, False, (0, 200, 0)]),
#             }
################################
# draw board
draw_board()
run = True
start_new_thread(threaded_listen, (n, ))
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
    pygame.display.update()
else:
    print("could not connect")

