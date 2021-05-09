import pygame
import numpy as np
from common import *
import subprocess
import glob
from network import Client


class Button:
    def __init__(self, text, pos, size, colourRange=(colours['btnEnabled'], colours['btnDisabled']), border=0, textSize=40, visible=True, enabled=True):
        self.text = text
        self.pos = pos
        self.size = size
        self.colourRange = colourRange  # (enabled colour, disabled colour)
        self.colour = None
        self.border = border
        self.enabled = enabled
        self.visible = visible
        self.textSize = textSize

    def draw(self, window):
        if self.visible:
            if self.enabled:
                self.colour = self.colourRange[0]
            else:
                self.colour = self.colourRange[1]
            pygame.draw.rect(window, self.colour, (self.pos[0], self.pos[1], self.size[0], self.size[1]), self.border)
            font = pygame.font.SysFont("freesans", self.textSize)
            text = font.render(self.text, True, (255, 255, 255))
            window.blit(text, (self.pos[0] + round(self.size[0]) / 2 - round(text.get_width() / 2),
                               self.pos[1] + round(self.size[1] / 2) - round(text.get_height() / 2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.pos[0] <= x1 <= self.pos[0] + self.size[0] and self.pos[1] <= y1 <= self.pos[1] + self.size[1] and self.enabled:
            return True
        else:
            return False


class CheckBox:
    def __init__(self, pos, width, enabled=True, checked=False):
        self.pos = pos
        self.width = width
        self.enabled = enabled
        self.checked = checked

        if self.width/10 >= 2:
            self.border = self.width / 10
        else:
            self.border = 2

    def draw(self, window):
        if self.enabled:
            pygame.draw.rect(window, colours['black'], (self.pos, [self.width]*2))
            pygame.draw.rect(window, colours['white'], ([self.pos[i] + self.border for i in range(2)], [self.width- 2 * self.border]*2))
            if self.checked:
                draw_asset(assets['cross'], tuple(self.pos[i] + self.width / 2 for i in range(2)), boundingBox=[self.width - 2.5 * self.border]*2)

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.pos[0] <= x1 <= self.pos[0] + self.width and self.pos[1] <= y1 <= self.pos[1] + self.width and self.enabled:
            self.checked = not self.checked
            self.draw(window)
            return True
        else:
            return False


class RadioButton:
    def __init__(self, options, pos, size=20, default=None, enabled=True):
        self.options = options
        self.pos = pos
        self.state = default
        self.size = size
        self.bufferSize = 5
        self.enabled = enabled

    def draw(self, window):
        self.draw_text(window)
        self.draw_buttons(window)

    def draw_text(self, window):
        x, y = self.pos
        for option in self.options:
            Text(str(option), (x + self.size + self.bufferSize, y), self.size).draw(window)
            y += (self.size + self.bufferSize)

    def draw_buttons(self, window):
        x, y = self.pos
        for i in range(len(self.options)):
            pygame.draw.circle(window, colours['black'], (x+self.size/2, y+self.size/2), self.size/2)
            if self.state == i:
                pygame.draw.circle(window, colours['orange'], (x+self.size/2, y+self.size/2), self.size/2-3)
            else:
                pygame.draw.circle(window, colours['white'], (x + self.size / 2, y + self.size / 2), self.size/2 - 3)
            y += (self.size + self.bufferSize)

    def click(self, clickPos):
        x, y = self.pos
        for i in range(len(self.options)):
            centre = (x+self.size/2, y+self.size/2)
            if (clickPos[0] - centre[0])**2 + (clickPos[1] - centre[1])**2 <= (self.size/2)**2:
                self.state = i
                self.draw_buttons(window)
                return True
            y += (self.size + self.bufferSize)
        return False


# class InputText:
# gets stuck in loop, not really needed anyways
#     def __init__(self, pos, length, textSize=20, promptText=""):
#         self.pos = pos
#         self.length = length
#         self.textSize = 20
#         self.border = 2
#         self.text = ""
#         self.active = True
#         self.promptText = promptText
#         self.size = (self.length, self.textSize + 4*self.border)
#
#     def draw(self, window):
#         pygame.draw.rect(window, colours['black'], (self.pos, self.size))
#         pygame.draw.rect(window, colours['white'], ([self.pos[i] + self.border for i in range(2)], (self.length - 2*self.border, self.textSize + 2*self.border)))
#         if self.text == "":
#             Text(self.promptText, [self.pos[i] + 2 * self.border for i in range(2)], self.textSize, colour=colours['grey']).draw(window)
#         else:
#             Text(self.text, [self.pos[i] + 2*self.border for i in range(2)], self.textSize).draw(window)
#
#
#     def click(self, pos):
#         x1 = pos[0]
#         y1 = pos[1]
#         if self.pos[0] <= x1 <= self.pos[0] + self.size[0] and self.pos[1] <= y1 <= self.pos[1] + self.size[1]:
#             self.active = True
#             return True
#         else:
#             self.active = False
#             return False
#
#     def write(self):
#         while self.active:
#             for event in pygame.event.get():
#                 if event.type == pygame.KEYDOWN:
#                     if event.key == pygame.K_RETURN:
#                         self.active = False
#                     elif event.key == pygame.K_BACKSPACE:
#                         self.text = self.text[:-1]
#                     else:
#                         self.text += event.unicode
#                         self.draw(window)

class Text:
    def __init__(self, text, pos, size, colour=colours['black'], bold=False, italic=False, visible=True):
        self.text = text
        self.pos = pos
        self.size = size
        self.colour = colour
        self.bold = bold
        self.italic = italic
        self.visible = visible

    def draw(self, window):
        if self.visible:
            font = pygame.font.SysFont("freesans", self.size, bold=self.bold, italic=self.italic)
            window.blit(font.render(self.text, True, self.colour), self.pos)


def draw_asset(asset, centre, scale=1.0, rotation=0.0, colour=colours['black'], lineWidth=0, boundingBox=None):
    def scale2fit(asset, boundingBox):
        assetSize = (max([vertex[0] for vertex in asset]) - min([vertex[0] for vertex in asset]),
                     max([vertex[1] for vertex in asset]) - min([vertex[1] for vertex in asset]))
        scales = (boundingBox[0] / assetSize[0], boundingBox[1] / assetSize[1])
        return min(scales)

    imgOut = []
    rotImg = []
    rotMatrix = np.array([[np.cos(rotation), -np.sin(rotation)],  # rotation matrix
                          [np.sin(rotation), np.cos(rotation)]])
    if boundingBox is not None:
        scale = scale2fit(asset, boundingBox)
    for vertex in asset:
        imgOut.append(np.add(rotMatrix.dot(vertex) * scale, centre))
    pygame.draw.polygon(window, colour, imgOut, width=lineWidth)


def welcome_screen():
    global clientID
    window.fill(colours['clientBackground'])
    run = True
    isUmpire = False

    texts = [Text("welcome to..", (4,0), 20, bold=True, italic=True),
             Text("Regatta 0.25", (4, 16), 40, bold=True, italic=True),
             Text("connect as umpire", (winSize[0]/2 - 32, winSize[1]/2 + 25), 10),
             Text("connection failed, retry", (winSize[0]/2 - 100, winSize[1] - 25), 20, colour=(255, 0, 0), visible=False)
             ]
    for text in texts:
        text.draw(window)

    BtnConnect = Button("connect", (winSize[0]/2 - 90, winSize[1]/2 - 20), (180, 40))
    BtnConnect.draw(window)
    ChkUmpire = CheckBox((winSize[0]/2 - 47, winSize[1]/2 + 25), 10)
    ChkUmpire.draw(window)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                clickPos = pygame.mouse.get_pos()
                if ChkUmpire.click(clickPos):
                    isUmpire = not isUmpire
                    print(isUmpire)

                if BtnConnect.click(clickPos):
                    try:
                        if isUmpire:
                            clientID = n.connect('umpire')
                        else:
                            clientID = n.connect('player')
                        print(clientID)
                        if n.connected:
                            print('connected')
                            texts[3].visible = False
                            texts[3].draw(window)
                    except Exception as e:
                        print(e)
                    if n.connected:
                    #     if isUmpire:
                    #         n.send('id', 'umpire')
                    #     else:
                    #         n.send('id', 'player')
                        return isUmpire
                    else:
                        print("connection failed, retry")
                        texts[3].visible = True
                        texts[3].draw(window)
        pygame.display.update()


def lobby_screen():
    def room():
        def draw_flotilla(flotilla, pos):
            xShift = 0
            for boat in flotilla:
                if boat[0] == clientID:
                    scale = 0.6
                else:
                    scale = 0.4
                draw_asset(assets['boat'], (pos[0] + xShift, pos[1]), scale, 0, boat[1])
                xShift += 40

        def threaded_listen():
            # listen for colour updates
            # update flotilla
            pass

        window.fill(colours['clientBackground'])
        texts = [Text("Game Lobby", (0, 0), 40, bold=True, italic=True),    # (245, 41)
                 Text("sail number:", (5, 51), 20),                         # (106, 20)
                 Text(str(clientID), (120, 46), 30),                           # (34, 30)
                 Text("pick boat colour:", (5, 81), 20),                  # (143, 20)
                 Text("flotilla:", (5, 200), 20),                           # (55, 20)
                 Text("ready?", (5, 350), 20)                               # (61, 21)
                 ]
        for text in texts:
            text.draw(window)

        colourBtns = []
        xShift = 0
        yShift = 0
        swatchSize = (25, 25)
        swatchSpacing = 30
        swatchPerRow = 8
        if len(boatColours) <= swatchPerRow:    #! could be neater
            swatchXOrigin = winSize[0]/2 - len(boatColours)/2 * swatchSize[0] - (len(boatColours) - 1)/2 * (swatchSpacing - swatchSize[0])
        else:
            swatchXOrigin = winSize[0]/2 - swatchPerRow/2 * swatchSize[0] - (swatchPerRow - 1)/2 * (swatchSpacing - swatchSize[0])
        for colour in boatColours:
            colourBtns.append(Button("", (swatchXOrigin + xShift, 111 + yShift), swatchSize, (colour, colours['btnDisabled'])))
            xShift += swatchSpacing
            if xShift >= swatchSpacing * swatchPerRow:
                xShift = 0
                yShift += swatchSpacing
        for btn in colourBtns:
            btn.draw(window)

        ChkReady = CheckBox((100, 400), 20)
        ChkReady.draw(window)
        ###########################################
        run = True
        flotilla = n.send('get', 'colours')
        print(flotilla)
        draw_flotilla(flotilla, (60, 175))

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    clickPos = pygame.mouse.get_pos()
                    for btn in colourBtns:
                        if btn.click(clickPos):
                            # n.send(btn.colour)
                            print(btn.colour)
                    if ChkReady.click(clickPos):
                        print("ready = " + str(ChkReady.checked))
                        # send "ready"
                        # get reply
                        print("waiting for other players")
                        # listen for "all ready"
                        return
            pygame.display.update()


def player_console():
    subprocess.Popen(['python', 'boardViewer.py'])
    run = True
    window.fill(colours['clientBackground'])

    point2arg = {}
    for i in range(8):
        point2arg.update({i: i*np.pi/4})
    wind = 0
    windArg = point2arg[wind]

    # compass rose
    roseCentre = (150, 250)
    offsetRoseCentre = tuple(i - 25 for i in roseCentre)
    roseRadius = 120
    compassRose = [Button("N", (offsetRoseCentre[0], offsetRoseCentre[1] - roseRadius), (50, 50)),
                   Button("NE", (offsetRoseCentre[0] + roseRadius*0.707, offsetRoseCentre[1] - roseRadius*0.707), (50, 50)),
                   Button("E", (offsetRoseCentre[0] + roseRadius, offsetRoseCentre[1]), (50, 50)),
                   Button("SE", (offsetRoseCentre[0] + roseRadius*0.707, offsetRoseCentre[1] + roseRadius*0.707), (50, 50)),
                   Button("S", (offsetRoseCentre[0], offsetRoseCentre[1] + roseRadius), (50, 50)),
                   Button("SW", (offsetRoseCentre[0] - roseRadius*0.707, offsetRoseCentre[1] + roseRadius*0.707), (50, 50)),
                   Button("W", (offsetRoseCentre[0] - roseRadius, offsetRoseCentre[1]), (50, 50)),
                   Button("NW", (offsetRoseCentre[0] - roseRadius*0.707, offsetRoseCentre[1] - roseRadius*0.707), (50, 50))
                   ]



    #sail controls
    sailControls = [Button("spin.", (42, 410), (100, 50)),
                    Button("puff", (147, 410), (100, 50)),
                    Button("port", (42, 465), (100, 50), colourRange=(colours['port'], colours['btnDisabled'])),
                    Button("star.", (147, 465), (100, 50), colourRange=(colours['starboard'], colours['btnDisabled']))
                    ]
    btnDice = Button("dice", (5, 5), (100, 50))
    btnEnd = Button("end turn", (42, 410), (205, 105), visible=False, enabled=False)

    buttonLookup = {'roll': btnDice,
                    'spin.': sailControls[0],
                    'puff': sailControls[1],
                    'P': sailControls[2],
                    'S': sailControls[3],
                    'end': btnEnd
                    }
    for i in range(len(compassRose)):
        buttonLookup.update({i: compassRose[i]})

    texts = [Text("puffs left: X", (195, 8), 20),   # (97, 20)
             Text("legs left: X", (203, 30), 20)]   # (89, 20)

    def draw_console(win):
        # get valid buttons
        validBtns = None
        while validBtns is None:
            validBtns = n.send('get', 'moves')
        # set usable buttons
        for btnKey in buttonLookup:
            if btnKey in validBtns:
                buttonLookup[btnKey].enabled = True
            else:
                buttonLookup[btnKey].enabled = False
        if btnEnd.enabled:
            btnEnd.visible = True
        else:
            btnEnd.visible = False

        # draw background
        window.fill(colours['clientBackground'])
        for text in texts:
            text.draw(win)

        # game controls
        btnEnd.draw(win)
        btnDice.draw(win)

        # sail controls
        for btn in sailControls:
            btn.draw(win)

        # compass rose
        pygame.draw.circle(window, colours['black'], roseCentre, roseRadius + 5)  # draw compass rose ring
        pygame.draw.circle(window, colours['clientBackground'], roseCentre, roseRadius - 5)
        for btn in compassRose:
            btn.draw(window)

        # wind arrow
        draw_asset(assets['windArrow'], roseCentre, rotation=windArg)

    ##########################################################
    draw_console(window)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                clickPos = pygame.mouse.get_pos()

                for btn in compassRose:
                    if btn.click(clickPos):
                        n.send('move', compassRose.index(btn))
                        print(compassRose.index(btn))

                for btn in sailControls:
                    if btn.click(clickPos):
                        if btn.text == 'port' or btn.text == 'star.':
                            n.send('move', 'tack')
                        else:
                            n.send('move', btn.text)
                        print(btn.text)

                if btnDice.click(clickPos):
                    n.send('move', 'roll')
                    print('roll dice')

                if btnEnd.click(clickPos):
                    n.send('move', 'end')
                    print('end turn')

                draw_console(window)


        pygame.display.update()


def umpire_setup():
    run = True
    window.fill(colours['clientBackground'])

    texts = [Text("pick map:", (0,0), 20)]
    for text in texts:
        text.draw(window)

    maps = glob.glob("boards/*.csv")    # assumes everyone has the same map files
    mapChoice = RadioButton(maps, (0, 0))
    mapChoice.draw(window)

    btnMake = Button("create room", (150, 100), (100, 50), enabled=False)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                clickPos = pygame.mouse.get_pos()
                if mapChoice.click(clickPos):
                    print(mapChoice.state)
                    if mapChoice.state is not None:
                        btnMake.enabled = True
                    else:
                        btnMake.enabled = False
                    btnMake.draw(window)

                if btnMake.click(clickPos):
                    n.send('make', ['boards/testMap.csv', None])
                    return

        pygame.display.update()


def umpire_console():
    run = True
    window.fill(colours['clientBackground'])

    raceFurniture = {'committee boat': [0, 0],
                     'buoy 1': [1, 1],
                     'buoy 2': [2, 2],
                     }

    RadBoats = RadioButton(list(raceFurniture.keys()), (0, 0), default=1)
    RadBoats.draw(window)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                clickPos = pygame.mouse.get_pos()
                if RadBoats.click(clickPos):
                    print(RadBoats.state)
        pygame.display.update()

########################################################################################################################
pygame.init()
winSize = (300, 520)
window = pygame.display.set_mode(winSize)
pygame.display.set_caption("client")
window.fill(colours['clientBackground'])
running = True
n = Client()
clientID = None
isUmpire = welcome_screen()
print(clientID)
while n.connected:
    if isUmpire:
        print("ump")
        umpire_setup()
        umpire_console()
    else:
        print("play")
        lobby_screen()
        player_console()
