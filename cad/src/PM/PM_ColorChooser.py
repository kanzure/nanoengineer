# Copyright 2006-2009 Nanorex, Inc.  See LICENSE file for details.
"""
PM_ColorChooser.py

@author: Mark
@version: $Id$
@copyright: 2006-2009 Nanorex, Inc.  All rights reserved.

History:

"""

from PyQt4.Qt import QLabel
from PyQt4.Qt import QFrame
from PyQt4.Qt import QToolButton
from PyQt4.Qt import QHBoxLayout
from PyQt4.Qt import QSpacerItem
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QWidget
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QColorDialog
from PyQt4.Qt import QPalette
from PyQt4.Qt import QSize

from utilities.constants import white, black
from widgets.widget_helpers import RGBf_to_QColor, QColor_to_RGBf

class PM_ColorChooser( QWidget ):
    """
    The PM_ColorChooser widget provides a color chooser widget for a
    Property Manager group box. The PM_ColorChooser widget is a composite widget
    made from 3 other Qt widgets:
    - a QLabel
    - a QFrame and
    - a QToolButton (with a "..." text label).

    IMAGE(http://www.nanoengineer-1.net/mediawiki/images/e/e2/PM_ColorChooser1.jpg)

    The user can color using Qt's color (chooser) dialog by clicking the "..."
    button. The selected color will be used as the color of the QFrame widget.

    The parent must make the following signal-slot connection to be
    notified when the user has selected a new color via the color chooser
    dialog:

    self.connect(pmColorChooser.colorFrame, SIGNAL("editingFinished()"), self.mySlotMethod)

    @cvar setAsDefault: Determines whether to reset the value of the
                        color to I{defaultColor} when the user clicks
                        the "Restore Defaults" button.
    @type setAsDefault: boolean

    @cvar labelWidget: The Qt label widget of this PM widget.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}

    @cvar colorFrame: The Qt frame widget for this PM widget.
    @type colorFrame: U{B{QFrame}<http://doc.trolltech.com/4/qframe.html>}

    @cvar chooseButton: The Qt tool button widget for this PM widget.
    @type chooseButton: U{B{QToolButton}<http://doc.trolltech.com/4/qtoolbutton.html>}
    """

    defaultColor = None
    setAsDefault = True
    hidden       = False
    chooseButton = None
    customColorCount  = 0
    standardColorList = [white, black]

    def __init__(self,
                 parentWidget,
                 label        = 'Color:',
                 labelColumn  = 0,
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

        @param color: initial color. White is the default.
        @type  color: tuple of 3 floats (r, g, b)

        @param setAsDefault: if True, will restore L{color} when the
                    "Restore Defaults" button is clicked.
        @type  setAsDefault: boolean

        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left
                      justified.
        @type  spanWidth: boolean

        @see: U{B{QColorDialog}<http://doc.trolltech.com/4/qcolordialog.html>}
        """

        QWidget.__init__(self)

        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.color        = color
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth

        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)

        # Create the color frame (color swath) and "..." button.
        self.colorFrame = QFrame()
        self.colorFrame.setFrameShape(QFrame.Box)
        self.colorFrame.setFrameShadow(QFrame.Plain)

        # Set browse button text and make signal-slot connection.
        self.chooseButton = QToolButton()
        self.chooseButton.setText("...")
        self.connect(self.chooseButton, SIGNAL("clicked()"), self.openColorChooserDialog)

        # Add a horizontal spacer to keep the colorFrame and "..." squeezed
        # together, even when the PM width changes.
        self.hSpacer = QSpacerItem(10, 10,
                                   QSizePolicy.MinimumExpanding,
                                   QSizePolicy.Fixed)

        # Create vertical box layout.
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setMargin(0)
        self.hBoxLayout.setSpacing(2)
        self.hBoxLayout.insertWidget(-1, self.colorFrame)
        self.hBoxLayout.insertWidget(-1, self.chooseButton)

        # Set this to False to make the colorFrame an expandable rectangle.
        COLORFRAME_IS_SQUARE = True
        if COLORFRAME_IS_SQUARE:
            squareSize = 20
            self.colorFrame.setMinimumSize(QSize(squareSize, squareSize))
            self.colorFrame.setMaximumSize(QSize(squareSize, squareSize))
            self.hBoxLayout.addItem(self.hSpacer)

        self.setColor(color, default = setAsDefault)

        parentWidget.addPmWidget(self)
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
        if default:
            self.defaultColor = color
            self.setAsDefault = default
        self.color = color
        self._updateColorFrame()
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

    def _updateColorFrame(self):
        """
        Updates the color frame with the current color.
        """
        colorframe = self.colorFrame
        try:
            qcolor = self.getQColor()
            palette = QPalette() # QPalette(qcolor) would have window color set from qcolor, but that doesn't help us here
            qcolorrole = QPalette.Window
                ## http://doc.trolltech.com/4.2/qpalette.html#ColorRole-enum says:
                ##   QPalette.Window    10    A general background color.
            palette.setColor(QPalette.Active, qcolorrole, qcolor) # used when window is in fg and has focus
            palette.setColor(QPalette.Inactive, qcolorrole, qcolor) # used when window is in bg or does not have focus
            palette.setColor(QPalette.Disabled, qcolorrole, qcolor) # used when widget is disabled
            colorframe.setPalette(palette)
            colorframe.setAutoFillBackground(True)
        except:
            print "data for following exception: ",
            print "colorframe %r has palette %r" % (colorframe, colorframe.palette())
        pass

    def openColorChooserDialog(self):
        """
        Prompts the user to choose a color and then updates colorFrame with
        the selected color.
        """
        qcolor = RGBf_to_QColor(self.color)
        if not self.color in self.standardColorList:
            QColorDialog.setCustomColor(self.customColorCount, qcolor.rgb())
            self.customColorCount += 1
        c = QColorDialog.getColor(qcolor, self)
        if c.isValid():
            self.setColor(QColor_to_RGBf(c))
            self.colorFrame.emit(SIGNAL("editingFinished()"))

    def restoreDefault(self):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setColor(self.defaultColor)
        return

    def hide(self):
        """
        Hides the lineedit and its label (if it has one).

        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget:
            self.labelWidget.hide()
        return

    def show(self):
        """
        Unhides the lineedit and its label (if it has one).

        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show()
        return

# End of PM_ColorChooser ############################


