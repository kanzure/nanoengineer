"""Various constants used in more than one module"""

leftButton = 1
rightButton = 2
midButton = 4
shiftButton = 256
cntlButton = 512

diDEFAULT = -1
diINVISIBLE = 0
diLINES = 1
diCPK = 2
diTUBES = 3
diVDW = 4

dispNames = ["def", 'nil', "lin", 'cpk', 'tub', 'vdw']

TubeRadius = 0.3

#colors
black = (0.0, 0.0, 0.0)
blue = (0.0,0.0,0.6)
aqua = (0.15, 1.0, 1.0)
orange = (1.0,0.25,0.0)
red = (1.0,0.0,0.0)
yellow = (1.0, 1.0, 0.0)
green = (0.0, 1.0, 0.0)
purple = (1.0, 0.0, 1.0)
white = (1.0,1.0,1.0)
gray = (0.5, 0.5, 0.5)

bondColor = (0.25, 0.25, 0.25)

PickedColor = (0.0, 0.0, 1.0)

globalParms = {}
globalParms['WorkingDirectory'] = "."

def logicColor(logic):
    if logic==0: return orange
    if logic==1: return aqua
    if logic==2: return yellow
