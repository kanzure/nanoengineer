# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.

"""
PM_Utilities.py

$Id$
"""

from PyQt4.QtGui import QSizePolicy

# Special Qt debugging functions written by Mark. 2007-05-24 ############

def getSizePolicyName(sizepolicy):
    """Returns the formal name of <sizepolicy>, a QSizePolicy.
    FYI:
    QSizePolicy.GrowFlag   = 1
    QSizePolicy.ExpandFlag = 2
    QSizePolicy.ShrinkFlag = 4
    QSizePolicy.IgnoreFlag = 8
    """
    assert isinstance(sizepolicy, QSizePolicy)

    if sizepolicy == QSizePolicy.Fixed:
        name = "SizePolicy.Fixed"
    if sizepolicy == QSizePolicy.GrowFlag:
        name = "SizePolicy.Minimum"
    if sizepolicy == QSizePolicy.ShrinkFlag:
        name = "SizePolicy.Maximum"
    if sizepolicy == (QSizePolicy.GrowFlag | QSizePolicy.ShrinkFlag):
        name = "SizePolicy.Preferred"
    if sizepolicy == (QSizePolicy.GrowFlag | QSizePolicy.ShrinkFlag |QSizePolicy.ExpandFlag):
        name = "SizePolicy.Expanding"
    if sizepolicy == (QSizePolicy.GrowFlag | QSizePolicy.ExpandFlag):
        name = "SizePolicy.MinimumExpanding"
    if sizepolicy == (QSizePolicy.ShrinkFlag | QSizePolicy.GrowFlag | QSizePolicy.IgnoreFlag):
        name = "SizePolicy.Ignored"
    return name

def printSizePolicy(widget):
    """Special method for debugging Qt sizePolicies.
    Prints the horizontal and vertical policy of <widget>.
    """
    sizePolicy = widget.sizePolicy()
    print "-----------------------------------"
    print "Widget name =", widget.objectName()
    print "Horizontal SizePolicy =", getSizePolicyName(sizePolicy.horizontalPolicy())
    print "Vertical SizePolicy =",   getSizePolicyName(sizePolicy.verticalPolicy()
    )
def printSizeHints(widget):
    """Special method for debugging Qt size hints.
    Prints the minimumSizeHint (width and height)
    and the sizeHint (width and height) of <widget>.
    """
    print "-----------------------------------"
    print "Widget name =", widget.objectName()
    print "Current Width, Height =", widget.width(), widget.height()
    minSize = widget.minimumSizeHint()
    print "Min Width, Height =", minSize.width(), minSize.height()
    sizeHint = widget.sizeHint()
    print "SizeHint Width, Height =", sizeHint.width(), sizeHint.height()