# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""Various constants used in more than one module
$Id$
"""
from qt import Qt

leftButton = 1
rightButton = 2
# in Qt/Mac, control key with left mouse button simulates right mouse button.
midButton = 4
shiftButton = 256
cntlButton = 512
# in Qt/Mac, this flag indicates the command key rather than the control key.

altButton = 1024 # in Qt/Mac, this flag indicates the Alt/Option modifier key.

# Note: it would be better if we replaced the above by the equivalent
# named constants provided by Qt. Before doing this, we have to find
# out how they correspond on each platform -- for example, I don't
# know whether Qt's named constant for the control key will have the
# same numeric value on Windows and Mac, as our own named constant
# 'cntlButton' does. So no one should replace the above numbers by
# Qt's declared names before they check this out on each platform. --
# bruce 040916


# debugButtons should be an unusual combination of modifier keys, used
# to bring up an undocumented debug menu intended just for developers
# (if a suitable preference is set). The following value is good for
# the Mac; someone on Windows or Linux can decide what value would be
# good for those platforms, and make this conditional on the
# platform. (If that's done, note that sys.platform on Mac might not
# be what you'd guess -- it can be either "darwin" or "mac" (I think),
# depending on the python installation.)  -- bruce 040916

debugButtons = cntlButton | shiftButton | altButton
# on the mac, this really means command-shift-alt


diDEFAULT = 0
diINVISIBLE = 1
diLINES = 2
diCPK = 3
diTUBES = 4
diVDW = 5

dispNames = ["def", "inv", "lin", "cpk", "tub", "vdw"]

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
               ('Si', Qt.Key_Q, 14),
               ('P', Qt.Key_P, 15),
               ('S', Qt.Key_S, 16),
               ('Cl', Qt.Key_L, 17)]
