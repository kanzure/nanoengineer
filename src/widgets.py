# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
'''
widgets.py

helpers for creating widgets, and some simple custom widgets

[owned by bruce, for now -- 041229]

$Id$
'''
__author__ = "bruce"

from PyQt4.Qt import *
from PyQt4 import QtGui
from qt4transition import *

# These don't exist in Qt4 but we can make begin(QVBox) and
# begin(QHBox) act the same as before.
QVBox, QHBox = range(2)

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
        self.layoutstack = [ ]
    def parent(self):
        """To use this widget_filler, create new widgets whose parent is what
        this method returns (always a qt widget, not a megawidget)
        [#e we might need a raw_parent method to return megawidgets directly]
        """
        # return qt_widget( self.where[-1] )
        return self.where[-1]

    class MyGroupBox(QGroupBox):
        pass

    def begin(self, thing):
        "use this to start a QVBox or QHBox, or a splitter; thing is the Qt widget class" #e or megawidget?
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
    "spinbox for a coordinate in angstroms -- permits negatives, floats"
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
    "checkbox, with configurable sense of whether checked means True or False"
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

# helper for making popup menus from our own "menu specs" description format,
# consisting of nested lists of text, callables or submenus, options.
# [moved here from GLPane.py -- bruce 050112]

def do_callable_for_undo(func, cmdname): #bruce 060324
    import undo_manager # important to do this here, since it might be reloaded before we get called
    import env
    from debug import print_compact_traceback
    assy = env.mainwindow().assy # needs review once we support multiple open files; caller might have to pass it in
    begin_retval = undo_manager.external_begin_cmd_checkpoint(assy, cmdname = cmdname)
    try:
        res = func() # i don't know if res matters to Qt
    except:
        print_compact_traceback("exception in menu command %r ignored: " % cmdname)
        res = None
    assy = env.mainwindow().assy # it might have changed!!! (in theory)
    undo_manager.external_end_cmd_checkpoint(assy, begin_retval)
    return res
    
def wrap_callable_for_undo(func, cmdname = "menu command"): #bruce 060324
    """Wrap a callable object func so that begin and end undo checkpoints are performed for it,
    and be sure the returned object can safely be called at any time in the future
    (even if various things have changed in the meantime).
       WARNING: If a reference needs to be kept to the returned object, that's the caller's responsibility.
    """
    # use 3 guards in case PyQt passes up to 3 unwanted args to menu callables,
    # and don't trust Python to preserve func and cmdname except in the lambda default values
    # (both of these precautions are generally needed or you can have bugs,
    #  when returning lambdas out of the defining scope of local variables they reference)
    return lambda _g1_ = None, _g2_ = None, _g3_ = None, func = func, cmdname = cmdname: do_callable_for_undo(func, cmdname)

def makemenu_helper(widget, menu_spec, menu = None):
    """Make and return a reusable or one-time-use (at caller's option)
    popup menu whose structure is specified by menu_spec,
    which is a list of menu item specifiers, each of which is either None
    (for a separator) or a tuple of the form (menu text, callable or submenu,
    option1, option2, ...) with 0 or more options (described below).
       A submenu can be either another menu_spec list, or a QMenu object
    (but in the latter case the menu text is ignored -- maybe it comes
    from that QMenu object somehow -- not sure if this was different in Qt3).
    In either case it is the 2nd menu-item-tuple element, in place of the callable.
       Otherwise the callable must satisfy the python 'callable' predicate,
    and is executed if the menu item is chosen, wrapped inside another function
    which handles Undo checkpointing and Undo-command-name setting.
       The options in a menu item tuple can be zero or more (in any order,
    duplicates allowed) of the following:
    'disabled' -- the menu item should be disabled;
    'checked' -- the menu item will be checked;
    None -- this option is legal but ignored (but the callable must still satisfy
    the python predicate "callable"; constants.noop might be useful for that case).
       The Qt3 version also supported tuple-options consisting of one of the words
    'iconset' and 'whatsThis' followed by an appropriate argument, but those have
    not yet been ported to Qt4 (except possibly for disabled menu items -- UNTESTED).
       Unrecognized options may or may not generate warnings, and are otherwise ignored.
    [###FIX that -- they always ought to print a warning to developers. Note that right
    now they do iff 'disabled' is one of the options and ATOM_DEBUG is set.]
       The 'widget' argument should be the Qt widget
    which is using this function to put up a menu.
       If the menu argument is provided, it should be a QMenu
    to which we'll add items; otherwise we create our own QMenu
    and add items to it.
    """
    from debug import print_compact_traceback
    import types
    if menu is None:
        menu = QMenu(widget)
        ## menu.show()
        #bruce 070514 removed menu.show() to fix a cosmetic and performance bug
        # (on Mac, possibly on other platforms too; probably unreported)
        # in which the debug menu first appears in screen center, slowly grows
        # to full size while remaining blank, then moves to its final position
        # and looks normal (causing a visual glitch, and a 2-3 second delay
        # in being able to use it). May fix similar issues with other menus.
        # If this causes harm for some menus or platforms, we can adapt it.
    # bruce 040909-16 moved this method from basicMode to GLPane,
    # leaving a delegator for it in basicMode.
    # (bruce was not the original author, but modified it)
    #menu = QMenu( widget)
    for m in menu_spec:
        try: #bruce 050416 added try/except as debug code and for safety
            menutext = m and widget.trUtf8(m[0])
            if m and isinstance(m[1], QMenu): #bruce 041010 added this case
                submenu = m[1]
                #menu.insertItem( menutext, submenu )
                menu.addMenu(submenu)   # how do I get menutext in there?
                    # (similar code might work for QAction case too, not sure)
            elif m and isinstance(m[1], types.ListType): #bruce 041103 added this case
                submenu = QMenu(menutext, menu)
                submenu = makemenu_helper(widget, m[1], submenu) # [this used to call widget.makemenu]
                menu.addMenu(submenu)
            elif m:
                assert callable(m[1]), \
                    "%r[1] needs to be a callable" % (m,) #bruce 041103
                # transform m[1] into a new callable that makes undo checkpoints and provides an undo command-name
                # [bruce 060324 for possible bugs in undo noticing cmenu items, and for the cmdnames]
                func = wrap_callable_for_undo(m[1], cmdname = m[0])
                    # guess about cmdname, but it might be reasonable for A7 as long as we ensure weird characters won't confuse it
                import changes
                changes.keep_forever(func) # THIS IS BAD (memory leak), but it's not a severe one, so ok for A7 [bruce 060324]
                    # (note: the hard part about removing these when we no longer need them is knowing when to do that
                    #  if the user ends up not selecting anything from the menu. Also, some callers make these
                    #  menus for reuse multiple times, and for them we never want to deallocate func even when some
                    #  menu command gets used. We could solve both of these by making the caller pass a place to keep these
                    #  which it would deallocate someday or which would ensure only one per distinct kind of menu is kept. #e)
                if 'disabled' not in m[2:]:
                    act = QAction(widget)
                    act.setText( menutext)
                    if 'checked' in m[2:]:
                        act.setCheckable(True)
                        act.setChecked(True)
                    menu.addAction(act)
                    widget.connect(act, SIGNAL("activated()"), func)
                else:
                    # disabled case
                    # [why is this case done differently, in this Qt4 port?? -- bruce 070522 question]
                    insert_command_into_menu(menu, menutext, func, options = m[2:], raw_command = True)
            else:
                menu.addSeparator() #bruce 070522 bugfix -- before this, separators were placed lower down or dropped
                    # so as not to come before disabled items, for unknown reasons.
                    # (Speculation: maybe because insertSeparator was used, since addSeparator didn't work or wasn't noticed,
                    #  and since disabled item were added by an older function (also for unknown reasons)?)
                pass
        except Exception, e:
            if isinstance(e, SystemExit):
                raise
            print_compact_traceback("exception in makemenu_helper ignored, for %r:\n" % (m,) )
                #bruce 070522 restored this (was skipped in Qt4 port)
            pass #e could add a fake menu item here as an error message
    return menu # from makemenu_helper

def insert_command_into_menu(menu, menutext, command, options = (), position = -1, raw_command = False, undo_cmdname = None): 
    """[This was part of makemenu_helper in the Qt3 version; in Qt4 it's only used for the disabled case,
     presumably for some good reason but not one which has been documented.]
    Insert a new item into menu (a QMenu), whose menutext, command, and options are as given,
    with undo_cmdname defaulting to menutext (used only if raw_command is false), 
    where options is a list or tuple in the same form as used in "menu_spec" lists
    such as are passed to makemenu_helper (which this function helps implement).
       The caller should have already translated/localized menutext if desired.
       If position is given, insert the new item at that position, otherwise at the end.
    Return the Qt menu item id of the new menu item.
    (I am not sure whether this remains valid if other items are inserted before it. ###k)
       If raw_command is False (default), this function will wrap command with standard logic for nE-1 menu commands
    (presently, wrap_callable_for_undo), and ensure that a python reference to the resulting callable is kept forever.
       If raw_command is True, this function will pass command unchanged into the menu,
    and the caller is responsible for retaining a Python reference to command.
       ###e This might need an argument for the path or function to be used to resolve icon filenames.
    """
    #bruce 060613 split this out of makemenu_helper.
    # Only called for len(options) > 0, though it presumably works
    # just as well for len 0 (try it sometime).
    import types
    from whatsthis import turn_featurenames_into_links, enable_whatsthis_links
    if not raw_command:
        command = wrap_callable_for_undo(command, cmdname = undo_cmdname or menutext)
        import changes
        changes.keep_forever(command)
            # see comments on similar code above about why this is bad in theory, but necessary and ok for now
    iconset = None
    for option in options:
        # some options have to be processed first
        # since they are only usable when the menu item is inserted. [bruce 050614]
        if type(option) is types.TupleType:
            if option[0] == 'iconset':
                # support iconset, pixmap, or pixmap filename [bruce 050614 new feature]
                iconset = option[1]
                if type(iconset) is types.StringType:
                    filename = iconset
                    from Utility import imagename_to_pixmap
                    iconset = imagename_to_pixmap(filename)
                if isinstance(iconset, QPixmap):
                    # (this is true for imagename_to_pixmap retval)
                    iconset = QIcon(iconset)
    if iconset is not None:
        import changes
        changes.keep_forever(iconset) #e memory leak; ought to make caller pass a place to keep it, or a unique id of what to keep
        #mitem_id = menu.insertItem( iconset, menutext, -1, position ) #bruce 050614, revised 060613 (added -1, position)
        mitem = menu.addAction( iconset, menutext ) #bruce 050614, revised 060613 (added -1, position)
            # Will this work with checkmark items? Yes, but it replaces the checkmark --
            # instead, the icon looks different for the checked item.
            # For the test case of gamess.png on Mac, the 'checked' item's icon
            # looked like a 3d-depressed button.
            # In the future we can tell the iconset what to display in each case
            # (see QIcon and/or QMenu docs, and helper funcs presently in debug_prefs.py.)
    else:
        # mitem_id = len(menu) -- mitem_id was previously an integer, indexing into the menu
        mitem = menu.addAction(menutext)
    for option in options:
        if option == 'checked':
            mitem.setChecked(True)
        elif option == 'unchecked': #bruce 050614 -- see what this does visually, if anything
            mitem.setChecked(False)
        elif option == 'disabled':
            mitem.setEnabled(False)
        elif type(option) is types.TupleType:
            if option[0] == 'whatsThis':
                txt = option[1]
                if enable_whatsthis_links:
                    txt = turn_featurenames_into_links(txt)
                mitem.setWhatsThis(txt)
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
        #e and something to use QMenuData.setShortcut
        #e and something to run whatever func you want on menu and mitem_id
    return mitem # from insert_command_into_menu

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
    from PyQt4.Qt import QColorDialog
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

def get_widget_with_color_palette(frame, color):
    ''' Return the widget with the background palette set to the 
    Qcolor provided by the user'''
    #ninad070502: This is used in many dialogs which show a colored frame 
    #that represents the current color of the object in the glpane. 
    #Example, in Rotary motor prop dialog, you will find a colored frame 
    #that shows the present color of the rotary motor. 
    frame.setAutoFillBackground(True)
    plt = QtGui.QPalette()      
    plt.setColor(QtGui.QPalette.Active,QtGui.QPalette.Window,color)
    plt.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.Window,color)
    plt.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.Window,color)
    frame.setPalette(plt)
    return frame

# ==

class TextMessageBox(QDialog):
    """The TextMessageBox class provides a modal dialog with a textedit widget 
    and a close button.  It is used as an option to QMessageBox when displaying 
    a large amount of text.  It also has the benefit of allowing the user to copy and 
    paste the text from the textedit widget.
    
    Call the setText() method to insert text into the textedit widget.
    """
    def __init__(self,parent = None,name = None,modal = 1,fl = 0):
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

        self.connect(self.close_button,SIGNAL("clicked()"),self.close)
        
    def setText(self, txt):
        "Sets the textedit's text to txt"
        self.text_edit.setPlainText(txt)

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
            "",
            1,  # The "default" button, when user presses Enter or Return (1 = Cancel)
            1)  # Escape (1= Cancel)
          
    if ret==0: 
        return True # Confirmed
    else:
        return False # Cancelled
            
# end
