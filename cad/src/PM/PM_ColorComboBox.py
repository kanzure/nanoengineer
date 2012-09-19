# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_ColorComboBox.py

@author: Mark
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  All rights reserved.

To do:
- Override addItem() and insertItem() methods.

"""

from PM.PM_ComboBox import PM_ComboBox

from PyQt4.Qt import QPixmap, QIcon, QColor, QSize
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QColorDialog

from utilities.constants import white, gray, black
from utilities.constants import red, orange, yellow
from utilities.constants import green, cyan, blue
from utilities.constants import magenta, violet, purple
from utilities.constants import darkred, darkorange, mustard
from utilities.constants import darkgreen, darkblue, darkpurple
from utilities.constants import lightgray
from widgets.widget_helpers import RGBf_to_QColor, QColor_to_RGBf

class PM_ColorComboBox( PM_ComboBox ):
    """
    The PM_ColorComboBox widget provides a combobox for selecting colors in a
    Property Manager group box.

    IMAGE(http://www.nanoengineer-1.net/mediawiki/images/e/e2/PM_ColorComboBox1.jpg)

    The parent must make the following signal-slot connection to be
    notified when the user has selected a new color:

    self.connect(pmColorComboBox, SIGNAL("editingFinished()"), self.mySlotMethod)

    @note: Subclasses L{PM_ComboBox}.
    """
    customColorCount  = 0
    color = None
    otherColor = lightgray
    otherColorList = [] # List of custom (other) colors the user has selected.

    colorList = [white, gray, black,
                 red, orange, yellow,
                 green, cyan, blue,
                 magenta, violet, purple,
                 darkred, darkorange, mustard,
                 darkgreen, darkblue, darkpurple,
                 otherColor]
    colorNames = ["White", "Gray", "Black",
                  "Red", "Orange", "Yellow",
                  "Green", "Cyan",
                  "Blue", "Magenta", "Violet", "Purple",
                  "Dark red", "Dark orange", "Mustard",
                  "Dark green", "Dark blue", "Dark purple",
                  "Other color..."]

    def __init__(self,
                 parentWidget,
                 label        = 'Color:',
                 labelColumn  = 0,
                 colorList    = [],
                 colorNames   = [],
                 color        = white,
                 setAsDefault = True,
                 spanWidth    = False,
                 ):
        """
        Appends a color chooser widget to <parentWidget>, a property manager
        group box.

        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox

        @param label: The label that appears to the left or right of the
                      color frame (and "Browse" button).

                      If spanWidth is True, the label will be displayed on
                      its own row directly above the lineedit (and button).

                      To suppress the label, set I{label} to an
                      empty string.
        @type  label: str

        @param labelColumn: The column number of the label in the group box
                            grid layout. The only valid values are 0 (left
                            column) and 1 (right column). The default is 0
                            (left column).
        @type  labelColumn: int

        @param colorList: List of colors.
        @type  colorList: List where each item contains 3 floats (r, g, b)

        @param colorNames: List of color names.
        @type  colorNames: List of strings

        @param color: The initial color. White is the default. If I{color}
                      is not in I{colorList}, then the initial color will be
                      set to the last color item (i.e. "Other color...").
        @type  color: tuple of 3 floats (r, g, b)

        @param setAsDefault: if True, will restore L{color} when the
                    "Restore Defaults" button is clicked.
        @type  setAsDefault: boolean

        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left
                      justified.
        @type  spanWidth: boolean
        """

        if len(colorNames) and len(colorList):
            assert len(colorNames) == len(colorList)
            self.colorNames = colorNames
            self.colorList  = colorList

        self.colorDict = dict(zip(self.colorNames, self.colorList))

        PM_ComboBox.__init__(self,
                 parentWidget,
                 label        = label,
                 labelColumn  = labelColumn,
                 choices      = self.colorNames,
                 index        = 0, # Gets (re)set by setColor()
                 setAsDefault = setAsDefault,
                 spanWidth    = spanWidth
                 )

        # Load QComboBox widget choices and set initial choice (index).
        idx = 0
        for colorName in self.colorNames:
            pixmap = QPixmap(12, 12)
            qcolor = RGBf_to_QColor(self.colorDict[str(colorName)])
            pixmap.fill(qcolor)
            self.setItemIcon(idx, QIcon(pixmap))
            idx += 1

        self.setIconSize(QSize(12, 12)) # Default is 16x16.
        self.setColor(color) # Sets current index.

        self.connect(self, SIGNAL("activated(QString)"), self._setColorFromName)

        return


    def _setColorFromName(self, colorName):
        """
        Set the color using the color index.

        @param colorName: The color name string.
        @type  colorName: str
        """
        if colorName == "Other color...":
            self.openColorChooserDialog() # Sets self.color
        else:
            self.setColor(self.colorDict[str(colorName)])
        return

    def setColor(self, color, default = False):
        """
        Set the color.

        @param color: The color.
        @type  color: tuple of 3 floats (r, g, b)

        @param default: If True, make I{color} the default color. Default is
                        False.
        @type  default: boolean
        """

        if color == self.color:
            return

        if default:
            self.defaultColor = color
            self.setAsDefault = default
        self.color = color

        try:
            # Try to set the current item to a color in the combobox.
            self.setCurrentIndex(self.colorList.index(color))
        except:
            # color was not in the combobox, so set current index to the last
            # item which is "Other color...". Also update the color icon to.
            otherColorIndex = len(self.colorList) - 1
            self.otherColor = color
            self.colorList[otherColorIndex] = color
            pixmap = QPixmap(16, 16)
            qcolor = RGBf_to_QColor(color)
            pixmap.fill(qcolor)
            self.setItemIcon(otherColorIndex, QIcon(pixmap))
            self.setCurrentIndex(self.colorList.index(self.otherColor))

        # Finally, emit a signal so the parent knows the color has changed.
        self.emit(SIGNAL("editingFinished()"))
        return

    def getColor(self):
        """
        Return the current color.

        @return: The current r, g, b color.
        @rtype:  Tuple of 3 floats (r, g, b)
        """
        return self.color

    def getQColor(self):
        """
        Return the current QColor.

        @return: The current color.
        @rtype:  QColor
        """
        return RGBf_to_QColor(self.color)

    def openColorChooserDialog(self):
        """
        Prompts the user to choose a color and then updates colorFrame with
        the selected color. Also sets self's I{color} attr to the selected
        color.
        """
        qcolor = RGBf_to_QColor(self.color)
        if not self.color in self.colorList[0:-1]:
            if not self.color in self.otherColorList:
                QColorDialog.setCustomColor(self.customColorCount, qcolor.rgb())
                self.otherColorList.append(self.color)
                self.customColorCount += 1
        c = QColorDialog.getColor(qcolor, self)
        if c.isValid():
            self.setColor(QColor_to_RGBf(c))
            self.emit(SIGNAL("editingFinished()"))

