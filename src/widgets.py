# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
widgets.py

helpers for creating widgets, and some simple custom widgets

[owned by bruce, for now -- 041229]

$Id$
'''
__author__ = "bruce"

from qt import QSpinBox, QDoubleValidator, QLabel, QCheckBox, QWidget, QPopupMenu, QAction, SIGNAL

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
        if self.label_prefix != None:
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

# helper for making popup menus from our own "menu specs"
# consisting of nested lists
# [moved here from GLPane.py -- bruce 050112]
# [should replace the one in modelTree with this one]

def makemenu_helper(self, lis):
    """make and return a reusable popup menu from lis,
    which gives pairs of command names and callables,
    or None for a separator.
    New feature [bruce 041010]:
    the "callable" can instead be a QPopupMenu object,
    or [bruce 041103] a list
    (indicating a menu spec like our 'lis' argument),
    to be used as a submenu.
       The 'self' argument should be the Qt widget
    which is using this function to put up a menu.
    """
    # bruce 040909-16 moved this method from basicMode to GLPane,
    # leaving a delegator for it in basicMode.
    # (bruce was not the original author, but modified it)
    win = self #e misnamed, should probably be widget #k
    menu = QPopupMenu(win)
    for m in lis:
        if m and isinstance(m[1], QPopupMenu): #bruce 041010 added this case
            submenu = m[1]
            menu.insertItem( win.trUtf8(m[0]), submenu )
                # (similar code might work for QAction case too, not sure)
        elif m and isinstance(m[1], type([])): #bruce 041103 added this case
            submenu = makemenu_helper(win, m[1]) # [used to call self.makemenu]
            menu.insertItem( win.trUtf8(m[0]), submenu )
        elif m:
            assert callable(m[1]), \
                "%r[1] needs to be a callable" % (m,) #bruce 041103
            if len(m) == 2:
                # old code
                # (this case might not be needed anymore, but it's known to work)
                act = QAction(win,m[0]+'Action')
                act.setText(win.trUtf8(m[0]))
                act.setMenuText(win.trUtf8(m[0]))
                act.addTo(menu)
                win.connect(act, SIGNAL("activated()"), m[1])
            else:
                # new code to support some additional menu item options
                # (likely to be expanded to support more).
                # Only used for len(m) > 2, though it presumably works
                # just as well for len 2 (try it sometime). [bruce 050112]
                mitem_id = menu.insertItem( win.trUtf8(m[0]) )
                menu.connectItem(mitem_id, m[1]) # semi-guess
                for option in m[2:]:
                    if option == 'checked':
                        menu.setItemChecked(mitem_id, True)
                    if option == 'disabled':
                        menu.setItemEnabled(mitem_id, False)
                    #e and something to use QMenuData.setAccel
                    #e and something to run whatever func you want on menu and mitem_id
                pass
        else:
            menu.insertSeparator()
    return menu

# end
