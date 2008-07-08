# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
widgets.py - helpers related to widgets, and some simple custom widgets.

@author: Mark, Ninad, perhaps others
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

TODO:

Probably should be split into a few modules (e.g. has several color-related
helpers).

[bruce 080203 has done some of this splitting but not all. I moved some of it
into undo_manager, some into a new module menu_helpers, and some into an
outtakes file "old_extrude_widgets.py".]

In the meantime we might rename it to widget_helpers.py.
"""

from PyQt4 import QtGui
from PyQt4.Qt import QDialog
from PyQt4.Qt import QVBoxLayout
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QString
from PyQt4.Qt import QValidator
from PyQt4.Qt import QColor
from PyQt4.Qt import QTextEdit
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QSize
from PyQt4.Qt import QMessageBox


from utilities.qt4transition import qt4todo

# ==

def double_fixup(validator, text, prevtext):
    """
    Returns a string that represents a float which meets the requirements of validator.
    text is the input string to be checked, prevtext is returned if text is not valid.
    """
    r, c = validator.validate(QString(text), 0)

    if r == QValidator.Invalid:
        return prevtext
    elif r == QValidator.Intermediate:
        if len(text) == 0:
            return ""
        return prevtext
    else:
        return text
        
# ==

# bruce 050614 [comment revised 050805] found colorchoose as a method in MWsemantics.py, nowhere used,
# so I moved it here for possible renovation and use.
# See also some color utilities in debug_prefs.py and prefs_widgets.py.
# Maybe some of them should all go into a new file specifically for colors. #e

def colorchoose(self, r, g, b):
    """
    #doc -- note that the args r,g,b should be ints, but the retval
    is a 3-tuple of floats. (Sorry, that's how I found it.)
    """
    # r, g, b is the default color displayed in the QColorDialog window.
    from PyQt4.Qt import QColorDialog
    color = QColorDialog.getColor(QColor(r, g, b), self, "choose") #k what does "choose" mean?
    if color.isValid():
        return color.red()/255.0, color.green()/255.0, color.blue()/255.0
    else:
        return r/255.0, g/255.0, b/255.0 # returning None might be more useful, since it lets callers "not change anything"
    pass

def RGBf_to_QColor(fcolor): # by Mark 050730
    """
    Converts RGB float to QColor.
    """
    # moved here by bruce 050805 since it requires QColor and is only useful with Qt widgets
    r = int (fcolor[0]*255 + 0.5) # (same formula as in elementSelector.py)
    g = int (fcolor[1]*255 + 0.5)
    b = int (fcolor[2]*255 + 0.5)
    return QColor(r, g, b)

def QColor_to_RGBf(qcolor): # by Mark 050921
    """
    Converts QColor to RGB float.
    """
    return qcolor.red()/255.0, qcolor.green()/255.0, qcolor.blue()/255.0

def QColor_to_Hex(qcolor): # by Mark 050921
    """
    Converts QColor to a hex color string. For example, a QColor of
    blue (0, 0, 255) returns "0000FF".
    """
    return "%02X%02X%02X" % (qcolor.red(), qcolor.green(), qcolor.blue())

def get_widget_with_color_palette(frame, color):
    """
    Return the widget <frame> after setting its palette based on <color>
    (a QColor provided by the user).
    """
    #ninad070502: This is used in many dialogs which show a colored frame 
    #that represents the current color of the object in the glpane. 
    #Example, in Rotary motor prop dialog, you will find a colored frame 
    #that shows the present color of the rotary motor. 
    frame.setAutoFillBackground(True)
    plt = QtGui.QPalette()      
    plt.setColor(QtGui.QPalette.Active,   QtGui.QPalette.Window, color)
    plt.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Window, color)
    plt.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Window, color)
    frame.setPalette(plt)
    return frame

# ==

class TextMessageBox(QDialog):
    """
    The TextMessageBox class provides a modal dialog with a textedit widget 
    and a close button.  It is used as an option to QMessageBox when displaying 
    a large amount of text.  It also has the benefit of allowing the user to copy and 
    paste the text from the textedit widget.
    
    Call the setText() method to insert text into the textedit widget.
    """
    def __init__(self, parent = None, name = None, modal = 1, fl = 0):
        #QDialog.__init__(self,parent,name,modal,fl)
        QDialog.__init__(self,parent)
        self.setModal(modal)
        qt4todo("handle flags in TextMessageBox.__init__")

        if name is None: name = "TextMessageBox"
        self.setObjectName(name)
        self.setWindowTitle(name)

        TextMessageLayout = QVBoxLayout(self)
        TextMessageLayout.setMargin(5)
        TextMessageLayout.setSpacing(1)
        
        self.text_edit = QTextEdit(self)

        TextMessageLayout.addWidget(self.text_edit)

        self.close_button = QPushButton(self)
        self.close_button.setText("Close")
        TextMessageLayout.addWidget(self.close_button)

        self.resize(QSize(350, 300).expandedTo(self.minimumSizeHint())) 
            # Width changed from 300 to 350. Now hscrollbar doesn't appear in
            # Help > Graphics Info textbox. mark 060322
        qt4todo('self.clearWState(Qt.WState_Polished)') # what is this?

        self.connect(self.close_button, SIGNAL("clicked()"),self.close)
        
    def setText(self, txt):
        """
        Sets the textedit's text to txt
        """
        self.text_edit.setPlainText(txt)

    pass

#==

def PleaseConfirmMsgBox(text = 'Please Confirm.'): # mark 060302.
    """
    Prompts the user to confirm/cancel by pressing a 'Confirm' or 'Cancel' button in a QMessageBox.
    <text> is the confirmation string to explain what the user is confirming.
    
    Returns:
        True - if the user pressed the Confirm button
        False - if the user pressed the Cancel button (or Enter, Return or Escape)
    """
    ret = QMessageBox.warning( None, "Please Confirm",
            str(text) + "\n",
            "Confirm",
            "Cancel", 
            "",
            1,  # The "default" button, when user presses Enter or Return (1 = Cancel)
            1)  # Escape (1= Cancel)
          
    if ret == 0: 
        return True # Confirmed
    else:
        return False # Cancelled
            
# end
