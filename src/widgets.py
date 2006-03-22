# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
widgets.py

helpers for creating widgets, and some simple custom widgets

[owned by bruce, for now -- 041229]

$Id$
'''
__author__ = "bruce"

from qt import *

def is_qt_widget(obj):
    return isinstance(obj, QWidget)

def qt_widget(obj):
    if is_qt_widget(obj):
        return obj
    else:
        # assume it's a megawidget
        return obj.widget
    pass

class widget_filler:
    """Helper class to make it more convenient to revise the code
    which creates nested widget structures (vbox, hbox, splitters, etc).
    For example of use, see extrudeMode.py.
    In the future we might also give this the power to let user prefs
    override the requested structure.
    """
    def __init__(self, parent, label_prefix = None, textfilter = None):
        """Parent should be the widget or megawidget to be filled with
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
    def parent(self):
        """To use this widget_filler, create new widgets whose parent is what
        this method returns (always a qt widget, not a megawidget)
        [#e we might need a raw_parent method to return megawidgets directly]
        """
        return qt_widget( self.where[-1] )
    def begin(self, thing):
        "use this to start a QVBox or QHBox, or a splitter; thing is the Qt widget class" #e or megawidget?
        box = thing(self.parent())
        self.where.append(box) #e for megawidgets, decide if we turn this to a qt widget now or on each use
        return 1
            # return value is so you can say "if begin(): ..." if you want to
            # use python indentation to show the widget nesting structure
    def end(self):
        self.where.pop()
    def label(self, text):
        if self.label_prefix is not None:
            name = self.label_prefix + text.strip()
        else:
            name = None #k ok?
        label = QLabel(self.parent(), name)
        if self.textfilter:
            text = self.textfilter(text)
        label.setText(text) # initial text
        return label # caller doesn't usually need this, except to vary the text
    pass

# these custom widgets were originally defined at the top of extrudeMode.py.

class FloatSpinBox(QSpinBox):
    "spinbox for a coordinate in angstroms -- permits negatives, floats"
    range_angstroms = 1000.0 # value can go to +- this many angstroms
    precision_angstroms = 100 # with this many detectable units per angstrom
    min_length = 0.1 # prevent problems with 0 or negative lengths provided by user
    max_length = 2 * range_angstroms # longer than possible from max xyz inputs
    def __init__(self, *args, **kws):
        #k why was i not allowed to put 'for_a_length = 0' into this arglist??
        for_a_length = kws.pop('for_a_length',0)
        assert not kws, "keyword arguments are not supported by QSpinBox"
        QSpinBox.__init__(self, *args) #k #e note, if the args can affect the range, we'll mess that up below
        ## self.setValidator(0) # no keystrokes are prevented from being entered
            ## TypeError: argument 1 of QSpinBox.setValidator() has an invalid type -- hmm, manual didn't think so -- try None? #e
        self.setValidator( QDoubleValidator( - self.range_angstroms, self.range_angstroms, 2, self ))
            # QDoubleValidator has a bug: it turns 10.2 into 10.19! But mostly it works. Someday we'll need our own. [bruce 041009]
        if not for_a_length:
            self.setRange( - int(self.range_angstroms * self.precision_angstroms),
                             int(self.range_angstroms * self.precision_angstroms) )
        else:
            self.setRange( int(self.min_length * self.precision_angstroms),
                           int(self.max_length * self.precision_angstroms) )
        self.setSteps( self.precision_angstroms, self.precision_angstroms * 10 ) # set linestep and pagestep
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
    "checkbox, with configurable sense of whether checked means True or False"
    def __init__(self, *args, **kws):
        self.sense = kws.pop('sense', True) # whether checking the box makes our value (seen by callers) True or False
        self.default = kws.pop('default', True) # whether our default value (*not* default checked-state) is True or False
        self.tooltip = kws.pop('tooltip', "") # tooltip to show ###e NIM
        # public attributes:
        self.attr = kws.pop('attr', None) # name of mode attribute (if any) which this should set
        self.repaintQ = kws.pop('repaintQ', False) # whether mode might need to repaint if this changes
        assert not kws, "keyword arguments are not supported by QCheckBox"
        QCheckBox.__init__(self, *args)
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

# helper for making popup menus from our own "menu specs" description format,
# consisting of nested lists of text, callables or submenus, options.
# [moved here from GLPane.py -- bruce 050112]

def makemenu_helper( widget, menu_spec):
    """make and return a reusable popup menu from menu_spec,
    which gives pairs of command names and callables,
    or None for a separator.
    New feature [bruce 041010]:
    the "callable" can instead be a QPopupMenu object,
    or [bruce 041103] a list
    (indicating a menu spec like our 'menu_spec' argument),
    to be used as a submenu.
       The 'widget' argument should be the Qt widget
    which is using this function to put up a menu.
    """
    from debug import print_compact_traceback
    # bruce 040909-16 moved this method from basicMode to GLPane,
    # leaving a delegator for it in basicMode.
    # (bruce was not the original author, but modified it)
    menu = QPopupMenu( widget)
    for m in menu_spec:
        try: #bruce 050416 added try/except as debug code and for safety
            if m and isinstance(m[1], QPopupMenu): #bruce 041010 added this case
                submenu = m[1]
                menu.insertItem( widget.trUtf8(m[0]), submenu )
                    # (similar code might work for QAction case too, not sure)
            elif m and isinstance(m[1], type([])): #bruce 041103 added this case
                submenu = makemenu_helper( widget, m[1]) # [used to call widget.makemenu]
                menu.insertItem( widget.trUtf8(m[0]), submenu )
            elif m:
                assert callable(m[1]), \
                    "%r[1] needs to be a callable" % (m,) #bruce 041103
                if len(m) == 2:
                    # old code
                    # (this case might not be needed anymore, but it's known to work)
                    act = QAction( widget,m[0]+'Action')
                    act.setText( widget.trUtf8(m[0]))
                    act.setMenuText( widget.trUtf8(m[0]))
                    act.addTo(menu)
                    widget.connect(act, SIGNAL("activated()"), m[1])
                else:
                    # new code to support some additional menu item options
                    # (likely to be expanded to support more).
                    # Only used for len(m) > 2, though it presumably works
                    # just as well for len 2 (try it sometime). [bruce 050112]
                    iconset = None
                    for option in m[2:]:
                        # some options have to be processed first
                        # since they are only usable when the menu item is inserted. [bruce 050614]
                        if type(option) == type((1,2)):
                            if option[0] == 'iconset':
                                # support iconset, pixmap, or pixmap filename [bruce 050614 new feature]
                                iconset = option[1]
                                if type(iconset) == type("filename"):
                                    filename = iconset
                                    from Utility import imagename_to_pixmap
                                    iconset = imagename_to_pixmap(filename)
                                if isinstance(iconset, QPixmap):
                                    # (this is true for imagename_to_pixmap retval)
                                    iconset = QIconSet(iconset)
                    if iconset is not None:
                        mitem_id = menu.insertItem( iconset, widget.trUtf8(m[0]) ) #bruce 050614
                            # Will this work with checkmark items? Yes, but it replaces the checkmark --
                            # instead, the icon looks different for the checked item.
                            # For the test case of gamess.png on Mac, the 'checked' item's icon
                            # looked like a 3d-depressed button.
                            # In the future we can tell the iconset what to display in each case
                            # (see QIconSet and/or QPopupMenu docs, and helper funcs presently in debug_prefs.py.)
                    else:
                        mitem_id = menu.insertItem( widget.trUtf8(m[0]) )
                    menu.connectItem(mitem_id, m[1]) # semi-guess
                    for option in m[2:]:
                        if option == 'checked':
                            menu.setItemChecked(mitem_id, True)
                        elif option == 'unchecked': #bruce 050614 -- see what this does visually, if anything ###k untested
                            menu.setItemChecked(mitem_id, False)
                        elif option == 'disabled':
                            menu.setItemEnabled(mitem_id, False)
                        elif type(option) == type((1,2)):
                            if option[0] == 'sbar': #bruce 050614 experiment; option is ('sbar', "explan for statusbar") ###k untested
                                menu.setWhatsThis(mitem_id, option[1])
                            elif option[0] == 'iconset':
                                pass # this was processed above
                            else:
                                if platform.atom_debug:
                                    print "atom_debug: fyi: don't understand menu_spec option %r", (option,)
                            pass
                        elif option is None:
                            pass # this is explicitly permitted and has no effect
                        else:
                            if platform.atom_debug:
                                print "atom_debug: fyi: don't understand menu_spec option %r", (option,)
                        pass
                        #e and something to use QMenuData.setAccel
                        #e and something to run whatever func you want on menu and mitem_id
                    pass
            else:
                menu.insertSeparator()
        except:
            print_compact_traceback("exception in makemenu_helper ignored, for %r:\n" % (m,) )
            pass #e could add a fake menu item here as an error message
    return menu

# ==

def double_fixup(validator, text, prevtext):
    '''Returns a string that represents a float which meets the requirements of validator.
    text is the input string to be checked, prevtext is returned if text is not valid.
    '''
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
    "#doc -- note that the args r,g,b should be ints, but the retval is a 3-tuple of floats. (Sorry, that's how I found it.)"
    # r, g, b is the default color displayed in the QColorDialog window.
    from qt import QColorDialog
    color = QColorDialog.getColor(QColor(r, g, b), self, "choose") #k what does "choose" mean?
    if color.isValid():
        return color.red()/255.0, color.green()/255.0, color.blue()/255.0
    else:
        return r/255.0, g/255.0, b/255.0 # returning None might be more useful, since it lets callers "not change anything"
    pass

def RGBf_to_QColor(fcolor): # by Mark 050730
    "Converts RGB float to QColor."
    # moved here by bruce 050805 since it requires QColor and is only useful with Qt widgets
    r = int (fcolor[0]*255 + 0.5) # (same formula as in elementSelector.py)
    g = int (fcolor[1]*255 + 0.5)
    b = int (fcolor[2]*255 + 0.5)
    return QColor(r, g, b)

def QColor_to_RGBf(qcolor): # by Mark 050921
    "Converts QColor to RGB float."
    return qcolor.red()/255.0, qcolor.green()/255.0, qcolor.blue()/255.0

# ==

class TextMessageBox(QDialog):
    """The TextMessageBox class provides a modal dialog with a textedit widget 
    and a close button.  It is used as an option to QMessageBox when displaying 
    a large amount of text.  It also has the benefit of allowing the user to copy and 
    paste the text from the textedit widget.
    
    Call the setText() method to insert text into the textedit widget.
    """
    def __init__(self,parent = None,name = None,modal = 1,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("TextMessageBox")

        TextMessageLayout = QGridLayout(self,1,1,5,-1,"TextMessageLayout")
        
        self.text_edit = QTextEdit(self,"text_edit")

        TextMessageLayout.addMultiCellWidget(self.text_edit,0,0,0,1)

        self.close_button = QPushButton(self,"close_button")
        self.close_button.setText("Close")
        TextMessageLayout.addWidget(self.close_button,1,1)
        
        spacer = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TextMessageLayout.addItem(spacer,1,0)

        self.resize(QSize(350, 300).expandedTo(self.minimumSizeHint())) 
            # Width changed from 300 to 350. Now hscrollbar doesn't appear in
            # Help > Graphics Info textbox. mark 060322
        self.clearWState(Qt.WState_Polished)

        self.connect(self.close_button,SIGNAL("clicked()"),self.close)
        
    def setText(self, txt):
        "Sets the textedit's text to txt"
        self.text_edit.setText(txt)

#==

def PleaseConfirmMsgBox(text='Please Confirm.'): # mark 060302.
    '''Prompts the user to confirm/cancel by pressing a 'Confirm' or 'Cancel' button in a QMessageBox.
    <text> is the confirmation string to explain what the user is confirming.
    
    Returns:
        True - if the user pressed the Confirm button
        False - if the user pressed the Cancel button (or Enter, Return or Escape)
    '''
    ret = QMessageBox.warning( None, "Please Confirm",
            str(text) + "\n",
            "Confirm",
            "Cancel", 
            None, 
            1,  # The "default" button, when user presses Enter or Return (1 = Cancel)
            1)  # Escape (1= Cancel)
          
    if ret==0: 
        return True # Confirmed
    else:
        return False # Cancelled
            
# end