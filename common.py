colours = {'sea': (80, 180, 255),
           'land': (20, 100, 40),
           'buoy': (255, 0, 0),
           'cboat': (255, 255, 255),
           'sfline': (135, 135, 135),
           'boat1': (0, 255, 0),
           'viewerBackground': (10, 120, 120),
           'btnEnabled': (0, 0, 0),
           'btnDisabled': (70, 70, 70),
           'black': (0, 0, 0),
           'grey': (150, 150, 150),
           'white': (255, 255, 255),
           'orange': (255,160, 0),
           'tail': (0, 200, 0),
           'blanketed': (64, 144, 204),
           'clientBackground': (150, 150, 150),
           'starboard': (30, 120, 30),
           'port': (180, 50, 40)
           }

boatColours = {'red': (200, 0, 0),
               'orange': (220, 125, 0),
               'yellow': (255, 250, 80),
               'darkGreen': (70, 110, 60),
               'turquoise': (50, 200, 180),
               'darkBlue': (20, 20, 100),
               'purple': (130, 40, 180),
               }

assets = {'windArrow': [(0, -64), (15, -40), (15, 40), (-15, 40), (-15, -40)],
          'boat': [(0, -50), (20, -15), (20, 40), (8, 50), (-8, 50), (-20, 40), (-20, -15)],
          'buoy': [(-54, 46), (46, 46), (48, 24), (33, 23), (33, -42), (-26, -48), (-36, 17), (-51, 16)],
          'cross': [(-10, -10), (-8, -10), (0, -3), (8, -10), (10, -10), (10, -8), (3, 0), (10, 8), (10, 10), (8, 10), (0, 3), (-8, 10), (-10, 10), (-10, 8), (-3, 0), (-10, -8)]
          }

point2sailing = {0: 0,
                 1: 1,
                 2: 2,
                 3: 3,
                 4: 2,
                 5: 3,
                 6: 2,
                 7: 1
                 }

point2vec = {0: (0, -1),
             1: (1, -1),
             2: (1, 0),
             3: (1, 1),
             4: (0, 1),
             5: (-1, 1),
             6: (-1, 0),
             7: (-1, -1)
             }


class Message:
    def __init__(self, messageType, data):
        self.messageType = messageType
        self.data = data

    def print(self):
        print([self.messageType, self.data])

    def read(self):
        return self.data
