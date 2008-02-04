# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
widgets.py - helpers for creating widgets, and some simple custom widgets.

@author: Bruce, Mark, Josh, perhaps others
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

TODO:

Probably should be split into a few modules (e.g. has several color-related
helpers). [bruce 080203 is doing this.]

Some things in here are no longer used.
"""

from PyQt4 import QtGui
from PyQt4.Qt import QGroupBox, QSpinBox, QCheckBox, QDialog
from PyQt4.Qt import QVBoxLayout
from PyQt4.Qt import QHBoxLayout
from PyQt4.Qt import QLabel
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QString
from PyQt4.Qt import QValidator
from PyQt4.Qt import QColor
from PyQt4.Qt import QTextEdit
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QSize
from PyQt4.Qt import QMessageBox


from qt4transition import qt4warning, qt4todo


# These don't exist in Qt4 but we can make begin(QVBox) and
# begin(QHBox) act the same as before.
QVBox, QHBox = range(2)

class widget_filler:
    """
    Helper class to make it more convenient to revise the code
    which creates nested widget structures (vbox, hbox, splitters, etc).
    For example of use, see extrudeMode.py.
    In the future we might also give this the power to let user prefs
    override the requested structure.
    """
    def __init__(self, parent, label_prefix = None, textfilter = None):
        """
        Parent should be the widget or megawidget to be filled with
        subwidgets using this widget_filler instance.
        """
        self.where = [parent]
            # stack of widgets or megawidgets currently being filled with subwidgets;
            # each one contains the next, and the last one (top of stack)
            # is the innermost one in the UI, which will contain newly
            # created widgets (assuming they specify self.parent() as
            # their parent).
        self.label_prefix = label_prefix
        self.textfilter = textfilter
        self.layoutstack = [ ]
    def parent(self):
        """
        To use this widget_filler, create new widgets whose parent is what
        this method returns (always a qt widget, not a megawidget)
        [#e we might need a raw_parent method to return megawidgets directly]
        """
        # return qt_widget( self.where[-1] )
        return self.where[-1]

    class MyGroupBox(QGroupBox):
        pass

    def begin(self, thing):
        """
        use this to start a QVBox or QHBox, or a splitter;
        thing is the Qt widget class
        """
        # someday: or can thing be a megawidget?
        assert thing in (QVBox, QHBox)
        if len(self.layoutstack) == len(self.where):
            grpbox = self.MyGroupBox()
            self.where.append(grpbox)
            self.layoutstack[-1].addWidget(grpbox)
        p = self.where[-1]
        if thing is QVBox:
            layoutklas = QVBoxLayout
        else:
            layoutklas = QHBoxLayout
        layout = layoutklas()
        self.layoutstack.append(layout)
        if len(self.where) > 1:
            p.setLayout(layout)
        if False:  # debug
            print '<<<'
            for x, y in map(None, self.where, self.layoutstack):
                print x, y
            print '>>>'
        return 1
        # return value is so you can say "if begin(): ..." if you want to
        # use python indentation to show the widget nesting structure

        # if this doesn't work, look at
        # PyQt-x11-gpl-4.0.1/examples/widgets/spinboxes.py

    def end(self):
        self.layoutstack.pop()
        if isinstance(self.where[-1], self.MyGroupBox):
            self.where.pop()
    def label(self, text):
        if self.label_prefix is not None:
            name = self.label_prefix + text.strip()
        else:
            name = None #k ok?
        #label = QLabel(self.parent(), name)
        label = QLabel(self.parent())  # ignore name for Qt 4
        if self.textfilter:
            text = self.textfilter(text)
        label.setText(text) # initial text
        return label # caller doesn't usually need this, except to vary the text
    pass

# these custom widgets were originally defined at the top of extrudeMode.py.

class FloatSpinBox(QSpinBox):
    """
    spinbox for a coordinate in angstroms -- permits negatives, floats
    """
    range_angstroms = 1000.0 # value can go to +- this many angstroms
    precision_angstroms = 100 # with this many detectable units per angstrom
    min_length = 0.1 # prevent problems with 0 or negative lengths provided by user
    max_length = 2 * range_angstroms # longer than possible from max xyz inputs
    def __init__(self, *args, **kws):
        #k why was i not allowed to put 'for_a_length = 0' into this arglist??
        for_a_length = kws.pop('for_a_length',0)
        assert not kws, "keyword arguments are not supported by QSpinBox"

        # QSpinBox.__init__(self, *args) #k #e note, if the args can affect the range, we'll mess that up below
        QSpinBox.__init__(self) #k #e note, if the args can affect the range, we'll mess that up below
        assert len(args) is 2
        assert type(args[1]) is type('abc')
        self.setObjectName(args[1])
        qt4warning('QSpinBox() ignoring args: ' + repr(args))

        ## self.setValidator(0) # no keystrokes are prevented from being entered
            ## TypeError: argument 1 of QSpinBox.setValidator() has an invalid type -- hmm, manual didn't think so -- try None? #e

        qt4todo('self.setValidator( QDoubleValidator( - self.range_angstroms, self.range_angstroms, 2, self ))')

            # QDoubleValidator has a bug: it turns 10.2 into 10.19! But mostly it works. Someday we'll need our own. [bruce 041009]
        if not for_a_length:
            self.setRange( - int(self.range_angstroms * self.precision_angstroms),
                             int(self.range_angstroms * self.precision_angstroms) )
        else:
            self.setRange( int(self.min_length * self.precision_angstroms),
                           int(self.max_length * self.precision_angstroms) )
        qt4todo('self.setSteps( self.precision_angstroms, self.precision_angstroms * 10 ) # set linestep and pagestep')

    def mapTextToValue(self):
        text = self.cleanText()
        text = str(text) # since it's a qt string
        ##print "fyi: float spinbox got text %r" % text
        try:
            fval = float(text)
            ival = int(fval * self.precision_angstroms) # 2-digit precision
            return ival, True
        except:
            return 0, False
    def mapValueToText(self, ival):
        fval = float(ival)/self.precision_angstroms
        return str(fval) #k should not need to make it a QString
    def floatValue(self):
        return float( self.value() ) / self.precision_angstroms
    def setFloatValue(self, fval):
        self.setValue( int( fval * self.precision_angstroms ) )
    pass

class TogglePrefCheckBox(QCheckBox):
    """
    checkbox, with configurable sense of whether checked means True or False
    """
    def __init__(self, *args, **kws):
        self.sense = kws.pop('sense', True) # whether checking the box makes our value (seen by callers) True or False
        self.default = kws.pop('default', True) # whether our default value (*not* default checked-state) is True or False
        self.tooltip = kws.pop('tooltip', "") # tooltip to show ###e NIM
        # public attributes:
        self.attr = kws.pop('attr', None) # name of mode attribute (if any) which this should set
        self.repaintQ = kws.pop('repaintQ', False) # whether mode might need to repaint if this changes
        assert not kws, "keyword arguments are not supported by QCheckBox"
        
        assert len(args) is 3
        assert type(args[0]) is type('abc')
        assert type(args[2]) is type('abc')        
        QCheckBox.__init__(self, args[0])
        
        self.setObjectName(args[2])
        #e set tooltip - how? see .py file made from .ui to find out (qt assistant didn't say).
    def value(self):
        if self.isChecked():
            return self.sense
        else:
            return not self.sense
    def setValue(self, bool1):
        if self.sense:
            self.setChecked( bool1)
        else:
            self.setChecked( not bool1)
    def initValue(self):
        self.setValue(self.default)
    pass

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
