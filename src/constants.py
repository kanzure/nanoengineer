# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""Various constants used in more than one module"""
from qt import Qt

leftButton = 1
rightButton = 2
midButton = 4
shiftButton = 256
cntlButton = 512

diDEFAULT = 0
diINVISIBLE = 1
diLINES = 2
diCPK = 3
diTUBES = 4
diMIXED = 5
diVDW = 6

dispNames = ["def", 'nil', "lin", 'cpk', 'tub', 'mix', 'vdw']

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
navy = (0.0, 0.09, 0.44)

LEDoff = (0.8, 0.0, 0.0)
LEDon = (1.0, 0.5, 0.5)

bondColor = (0.25, 0.25, 0.25)

PickedColor = (0.0, 0.0, 1.0)

globalParms = {}
globalParms['WorkingDirectory'] = "."

def logicColor(logic):
    if logic==0: return orange
    if logic==1: return navy
    if logic==2: return yellow

assyList = []

elemKeyTab =  [('H', Qt.Key_H, 1),
               ('B', Qt.Key_B, 5),
               ('C', Qt.Key_C, 6),
               ('N', Qt.Key_N, 7),
               ('O', Qt.Key_O, 8),
               ('F', Qt.Key_F, 9),
               ('Al', Qt.Key_A, 13),
               ('Si', Qt.Key_I, 14),
               ('P', Qt.Key_P, 15),
               ('S', Qt.Key_S, 16),
               ('Cl', Qt.Key_L, 17)]

