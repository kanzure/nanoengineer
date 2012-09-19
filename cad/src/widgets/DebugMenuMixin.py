# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
Mixin class to help some of our widgets offer a debug menu.

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

Needs refactoring:  [bruce 080104]

- to move the global variable (sim_params_set) elsewhere
(and maybe a lot of the surrounding code too -- I didn't analyze it)

- maybe to permit or require host widget to supply some items --
see classification comment below.

Module classification:  [bruce 080104]

Essentially this is a "widget helper" to let a widget provide a
"standard debug menu". It also includes a lot of the specific
menu items and their implementations, even some that only work
in some widgets. For now I'll classify it in "widgets" due to
its widget helper role. Ideally we'd refactor it in such a way
that that was completely accurate (moving the rest into the
specific widgets or into other modules which register items
for general use in this menu).
"""

import sys
import time

from PyQt4.Qt import QDialog, QGridLayout, QLabel, QPushButton, QLineEdit, SIGNAL
from PyQt4.Qt import QFontDialog, QInputDialog

import foundation.env as env
from utilities import debug_flags
import utilities.debug as debug
import utilities.debug_prefs as debug_prefs

from ne1_ui.prefs.Preferences import save_window_pos_size, load_window_pos_size
from utilities.prefs_constants import mainwindow_geometry_prefs_key_prefix
from utilities.debug import registered_commands_menuspec
from utilities.debug import print_compact_traceback
from utilities.debug import debug_timing_test_pycode_from_a_dialog
from utilities.debug import debug_run_command
from utilities.constants import debugModifiers
from utilities.constants import noop
from time import clock
from utilities.debug import profile_single_call_if_enabled, set_enabled_for_profile_single_call
from widgets.simple_dialogs import grab_text_line_using_dialog

# enable the undocumented debug menu by default [bruce 040920]
# (moved here from GLPane, now applies to all widgets using DebugMenuMixin [bruce 050112])
debug_menu_enabled = 1
debug_events = 0 # set this to 1 to print info about many mouse events

# this can probably be made a method on DebugMenuMixin
def debug_runpycode_from_a_dialog( source = "some debug menu??"):
    # TODO: rewrite this to call grab_text_using_dialog (should be easy)
    title = "debug: run py code"
    label = "one line of python to exec in debug.py's globals()\n(or use @@@ to fake \\n for more lines)\n(or use execfile)"
    parent = None
        #bruce 070329 Qt4 bugfix -- in Qt4 a new first argument (parent) is needed by QInputDialog.getText.
        # [FYI, for a useful reference to QInputDialog with lots of extra info, see
        #  http://www.bessrc.aps.anl.gov/software/qt4-x11-4.2.2-browser/d9/dcb/class_q_input_dialog.html ]
    text, ok = QInputDialog.getText(parent, title, label)
    if ok:
        # fyi: type(text) == <class '__main__.qt.QString'>
        command = str(text)
        command = command.replace("@@@",'\n')
        debug_run_command(command, source = source)
    else:
        print "run py code: cancelled"
    return

class DebugMenuMixin:
    """
    Helps widgets have the "standard undocumented debug menu".
    Provides some methods and attrs to its subclasses,
    all starting debug or _debug, especially self.debug_event().
    Caller of _init1 should provide main window win, or [temporary kluge?]
    let this be found at self.win; some menu items affect it or emit
    history messages to it.
    [As of 050913 they should (and probably do) no longer use win for history,
    but use env.history instead.]
    """
    #doc better
    #e rename private attrs to start with '_debug' instead of 'debug'
    #e generalize so the debug menu can be customized? not sure it's needed.

    ## debug_menu = None # needed for use before _init1 or if that fails

    def _init1(self, win = None):
        # figure out this mixin's idea of main window
        if not win:
            try:
                self.win # no need: assert isinstance( self.win, QWidget)
            except AttributeError:
                pass
            else:
                win = self.win
        self._debug_win = win
        # figure out classname for #doc
        try:
            self._debug_classname = "class " + self.__class__.__name__
        except:
            self._debug_classname = "<some class>"
        # make the menu -- now done each time it's needed
        return

    def makemenu(self, menu_spec, menu = None):
        """
        Make and return a menu object for use in this widget, from the given menu_spec.
        If menu is provided (should be a QMenu), append to it instead.
        For more info see docstring of widgets.menu_helpers.makemenu_helper.

        [This can be overridden by a subclass, but probably never needs to be,
        unless it needs to make *all* menus differently (thus we do use the overridden
        version if one is present) or unless it uses it independently from this mixin
        and wants to be self-contained.]
        """
        from widgets.menu_helpers import makemenu_helper
        return makemenu_helper(self, menu_spec, menu)

    def debug_menu_items(self):
        """
        #doc; as of 050416 this will be called every time the debug menu needs to be put up,
        so that the menu contents can be different each time (i.e. so it can be a dynamic menu)
        [subclasses can override this; best if they call this superclass method
        and modify its result, e.g. add new items at top or bottom]
        """
        res = [
            ('debugging menu (unsupported)', noop, 'disabled'), #bruce 060327 revised text
            # None, # separator
        ]
        if 0 and self._debug_win: #bruce 060327 disabled this, superseded by prefs dialog some time ago
            res.extend( [
                ('load window layout', self._debug_load_window_layout ),
                ('save window layout', self._debug_save_window_layout ),
                #bruce 050117 prototype "save window layout" here; when it works, move it elsewhere
            ] )
        if debug.exec_allowed():
            #bruce 041217 made this item conditional on whether it will work
            res.extend( [
                ('run py code', self._debug_runpycode),
                ('sim param dialog', self._debug_sim_param_dialog),
                ('force sponsor download', self._debug_force_sponsor_download),
                ('speed-test py code', self._debug_timepycode), #bruce 051117; include this even if not debug_flags.atom_debug
            ] )
        #bruce 050416: use a "checkmark item" now that we're remaking this menu dynamically:
        if debug_flags.atom_debug:
            res.extend( [
                ('ATOM_DEBUG', self._debug_disable_atom_debug, 'checked' ),
            ] )
        else:
            res.extend( [
                ('ATOM_DEBUG', self._debug_enable_atom_debug ),
            ] )

        #bruce 060124 changes: always call debug_prefs_menuspec, but pass debug_flags.atom_debug to filter the prefs,
        # and change API to return a list of menu items (perhaps empty) rather than exactly one
        res.extend( debug_prefs.debug_prefs_menuspec( debug_flags.atom_debug ) ) #bruce 050614 (submenu)

        if 1: #bruce 050823
            some = registered_commands_menuspec( self)
            res.extend(some)

        res.extend( [
            ('choose font', self._debug_choose_font),
        ] )
        if self._debug_win:
            res.extend( [
                ('call update_parts()', self._debug_update_parts ), ###e also should offer check_parts
            ] )

        if 1: #bruce 060327; don't show them in the menu itself, we need to see them in time, in history, with and without atom_debug
            res.extend( [
                ('print object counts', self._debug_print_object_counts),
            ] )


        if 1: #piotr 080311: simple graphics benchmark
            res.extend( [
                ('measure graphics performance', self._debug_do_benchmark),
            ] )

        #command entered profiling
        res.extend( [
            ('Profile entering a command...',
             self._debug_profile_userEnterCommand),
            ('(print profile output)',
             self._debug_print_profile_output),
        ] )


        if debug_flags.atom_debug: # since it's a dangerous command
            res.extend( [
                ('debug._widget = this widget', self._debug_set_widget),
                ('destroy this widget', self._debug_destroy_self),
            ] )
        res.extend( [
            ('print self', self._debug_printself),
        ] )
        return res

    def _debug_save_window_layout(self): # [see also Preferences.save_current_win_pos_and_size, new as of 051218]
        win = self._debug_win
        keyprefix = mainwindow_geometry_prefs_key_prefix
        save_window_pos_size( win, keyprefix)

    def _debug_load_window_layout(self): # [similar code is in pre_main_show in a startup module, new as of 051218]
        win = self._debug_win
        keyprefix = mainwindow_geometry_prefs_key_prefix
        load_window_pos_size( win, keyprefix)

    def _debug_update_parts(self):
        win = self._debug_win
        win.assy.update_parts()

    def _debug_print_object_counts(self):
        #bruce 060327 for debugging memory leaks: report Atom & Bond refcounts, and objs that might refer to them
        # Note: these counts include not only instances, but imports of classes into modules.
        # That's probably why the initial counts seem too high:
        # 40 Atoms, 24 Bonds, 40 Chunks, 34 Groups, 8 Parts, 10 Assemblies
        # [as of 080403]
        from utilities.Log import _graymsg
        msglater = "" # things to print all in one line
        for clasname, modulename in (
            #bruce 080403 fixed modulenames (since the modules were moved into
            # packages); the dotted names seem to work.
            ('Atom', 'model.chem'),
            ('Bond', 'model.bonds'),
            # ('Node', 'Utility'), # Node or Jig is useless here, we need the specific subclasses!
            ('Chunk', 'model.chunk'),
            # DnaLadderRailChunk
            ## ('PiBondSpChain', 'pi_bond_sp_chain'), # no module pi_bond_sp_chain -- due to lazy load or atom-debug reload??
            ('Group', 'foundation.Group'), # doesn't cover subclasses PartGroup, ClipboardItemGroup, RootGroup(sp?), Dna groups
            ('Part', 'model.part'),
            ('Assembly', 'model.assembly')):
            # should also have a command to look for other classes with high refcounts
            if sys.modules.has_key(modulename):
                module = sys.modules[modulename]
                clas = getattr(module, clasname, None)
                if clas:
                    msg = "%d %ss" % (sys.getrefcount(clas), clasname)
                    msg = msg.replace("ys","ies") # for spelling of Assemblies
                    # print these things all at once
                    if msglater:
                        msglater += ', '
                    msglater += msg
                    msg = None
                else:
                    msg = "%s not found in %s" % (clasname, modulename)
            else:
                msg = "no module %s" % (modulename,)
            if msg:
                env.history.message( _graymsg( msg))
        if msglater:
            env.history.message( _graymsg( msglater))
        return

    def _debug_choose_font(self): #bruce 050304 experiment; works; could use toString/fromString to store it in prefs...
        oldfont = self.font()
        newfont, ok = QFontDialog.getFont(oldfont)
            ##e can we change QFontDialog to let us provide initial sample text,
            # and permit typing \n into it? If not, can we fool it by providing
            # it with a fake "paste" event?
        if ok:
            self.setFont(newfont)
            try:
                if debug_flags.atom_debug:
                    print "atom_debug: new font.toString():", newfont.toString()
            except:
                print_compact_traceback("new font.toString() failed: ")
        return

    def _debug_enable_atom_debug(self):
        debug_flags.atom_debug = 1

    def _debug_disable_atom_debug(self):
        debug_flags.atom_debug = 0

    def debug_event(self, event, funcname, permit_debug_menu_popup = 0): #bruce 040916
        """
        [the main public method for subclasses]

        Debugging method -- no effect on normal users.  Does two
        things -- if a global flag is set, prints info about the
        event; if a certain modifier key combination is pressed,
        and if caller passed permit_debug_menu_popup = 1, puts up
        an undocumented debugging menu, and returns 1 to caller.

        Modifier keys to bring it up:
        Mac: Shift-Option-Command-click
        Linux: <cntrl><shift><alt><left click>
        Windows: probably same as linux
        """
        # In constants.py: debugModifiers = cntlModifier | shiftModifier | altModifier
        # On the mac, this really means command-shift-alt [alt == option].
        if debug_menu_enabled and permit_debug_menu_popup and \
           int(event.modifiers() & debugModifiers) == debugModifiers:
            ## print "\n* * * fyi: got debug click, will try to put up a debug menu...\n" # bruce 050316 removing this
            self.do_debug_menu(event)
            return 1 # caller should detect this and not run its usual event code...
        if debug_events:
            try:
                before = event.state()
            except:
                before = "<no state>" # needed for Wheel events, at least
            try:
                after = event.stateAfter()
            except:
                after = "<no stateAfter>" # needed for Wheel events, at least
            print "%s: event; state = %r, stateAfter = %r; time = %r" % (funcname, before, after, time.asctime())

        # It seems, from doc and experiments, that event.state() is
        # from just before the event (e.g. a button press or release,
        # or move), and event.stateAfter() is from just after it, so
        # they differ in one bit which is the button whose state
        # changed (if any).  But the doc is vague, and the experiments
        # incomplete, so there is no guarantee that they don't
        # sometimes differ in other ways.
        # -- bruce ca. 040916
        return 0

    def do_debug_menu(self, event):
        """
        [public method for subclasses]
        #doc
        """
        ## menu = self.debug_menu
        #bruce 050416: remake the menu each time it's needed
        menu_spec = None
        try:
            menu_spec = self.debug_menu_items()
            menu = self.makemenu(menu_spec, None)
            if menu: # might be []
                menu.exec_(event.globalPos())
        except:
            print_compact_traceback("bug in do_debug_menu ignored; menu_spec is %r" % (menu_spec,) )

    def _debug_printself(self):
        print self

    def _debug_set_widget(self): #bruce 050604
        debug._widget = self
        print "set debug._widget to",self

    def _debug_destroy_self(self): #bruce 050604
        #e should get user confirmation
        ## self.destroy() ###k this doesn't seem to work. check method name.
        self.deleteLater()

    def _draw_hundred_frames(self, par1, par2):
        # redraw 100 frames, piotr 080403
        for i in range(0, 100):
            self.win.glpane.paintGL() # BUG; see below. [bruce 090305 comment]

    def _debug_do_benchmark(self):
        # simple graphics benchmark, piotr 080311
        from time import clock
        print "Entering graphics benchmark. Drawing 100 frames... please wait."
        win = self._debug_win
        self.win.resize(1024,768) # resize the window to a constant size

        self.win.glpane.paintGL()
        # draw once just to make sure the GL context is current
        # piotr 080405
        # [BUG: the right way is gl_update -- direct call of paintGL won't
        #  always work, context might not be current -- bruce 090305 comment]

        env.call_qApp_processEvents() # make sure all events were processed
        tm0 = clock()
        profile_single_call_if_enabled(self._draw_hundred_frames, self, None)
        tm1 = clock()
        print "Benchmark complete. FPS = ", 100.0 / (tm1 - tm0)
        return

    def _debug_profile_userEnterCommand(self):
        """
        Debug menu command for profiling userEnterCommand(commandName).

        This creates a profile.output file on each use
        (replacing a prior one if any, even if it was created
        during the same session).

        Note that for some commands, a lot more work will be done the
        first time they are entered during a session (or in some cases,
        the first time since opening a new file) than in subsequent times.
        """
        # Ninad 2008-10-03; renamed/revised by bruce 090305

        RECOGNIZED_COMMAND_NAMES = (
            'DEPOSIT',
            'BUILD_DNA',
            'DNA_SEGMENT',
            'DNA_STRAND',
            'CRYSTAL',
            'BUILD_NANOTUBE',
            'EDIT_NANOTUBE',
            'EXTRUDE',
            'MODIFY',
            'MOVIE'
         )

        ok, commandName =  grab_text_line_using_dialog(
            title = "profile entering given command",
            label = "Enter the command.commandName e.g. 'BUILD_DNA' , 'DEPOSIT'"
         )
        if not ok:
            print "No command name entered, returning"
            return

        commandName = str(commandName)
        commandName = commandName.upper()
        if not commandName in RECOGNIZED_COMMAND_NAMES:
            #bruce 090305 changed this to just a warning, added try/except
            print "Warning: command name %r might or might not work. " \
                  "Trying it anyway." % (commandName,)
            pass

        print "Profiling command enter for %s" % (commandName,)

        win = self._debug_win
        meth = self.win.commandSequencer.userEnterCommand
        set_enabled_for_profile_single_call(True)
        tm0 = clock()
        try:
            profile_single_call_if_enabled(meth, commandName)
        except:
            print "exception entering command caught and discarded." #e improve
            sys.stdout.flush()
            pass
        tm1 = clock()
        set_enabled_for_profile_single_call(False)
        print "Profiling complete. Total CPU time to enter %s = %s" % \
              (commandName, (tm1 - tm0))
        return

    def _debug_print_profile_output(self): #bruce 090305
        """
        """
        # todo: improve printing options used inside the following
        debug.print_profile_output()
        return

    def debug_menu_source_name(self): #bruce 050112
        """
        can be overriden by subclasses
        #doc more
        """
        try:
            return "%s debug menu" % self.__class__.__name__
        except:
            return "some debug menu"

    def _debug_runpycode(self):
        debug_runpycode_from_a_dialog( source = self.debug_menu_source_name() )
            # e.g. "GLPane debug menu"
        return

    def _debug_sim_param_dialog(self):
        global _sim_parameter_dialog
        if _sim_parameter_dialog is None:
            _sim_parameter_dialog = SimParameterDialog()
        _sim_parameter_dialog.show()
        return

    def _debug_force_sponsor_download(self):
        from sponsors.Sponsors import _force_download
        _force_download()
        return

    def _debug_timepycode(self): #bruce 051117
        debug_timing_test_pycode_from_a_dialog( )
        return

    pass # end of class DebugMenuMixin

##########################################################

BOOLEAN = "boolean"
INT = "int"
FLOAT = "float"
STRING = "string"

sim_params_set = False

# We get mysterious core dumps if we turn all these other guys on. We
# didn't have time before the A8 release to investigate the matter in
# depth, so we just switched off the ones we didn't need immediately.

_sim_param_table = [
    ("debug_flags", INT),
    # ("IterPerFrame", INT),
    # ("NumFrames", INT),
    # ("DumpAsText", BOOLEAN),
    # ("DumpIntermediateText", BOOLEAN),
    # ("PrintFrameNums", BOOLEAN),
    # ("OutputFormat", INT),
    # ("KeyRecordInterval", INT),
    # ("DirectEvaluate", BOOLEAN),
    # ("IDKey", STRING),
    # ("Dt", FLOAT),
    # ("Dx", FLOAT),
    # ("Dmass", FLOAT),
    # ("Temperature", FLOAT),
]

sim_param_values = {
    "debug_flags": 0,
    # "IterPerFrame": 10,
    # "NumFrames": 100,
    # "DumpAsText": False,
    # "DumpIntermediateText": False,
    # "PrintFrameNums": True,
    # "OutputFormat": 1,
    # "KeyRecordInterval": 32,
    # "DirectEvaluate": False,
    # "IDKey": "",
    # "Dt": 1.0e-16,
    # "Dx": 1.0e-12,
    # "Dmass": 1.0e-27,
    # "Temperature": 300.0,
}

class SimParameterDialog(QDialog):

    def __init__(self, win = None):
        import string
        QDialog.__init__(self, win)
        self.setWindowTitle('Manually edit sim parameters')
        layout = QGridLayout(self)
        layout.setMargin(1)
        layout.setSpacing(-1)
        layout.setObjectName("SimParameterDialog")
        for i in range(len(_sim_param_table)):
            attr, paramtype = _sim_param_table[i]
            current = sim_param_values[attr]
            currentStr = str(current)
            label = QLabel(attr + ' (' + paramtype + ')', self)
            layout.addWidget(label, i, 0)
            if paramtype == BOOLEAN:
                label = QLabel(currentStr, self)
                layout.addWidget(label, i, 1)
                def falseFunc(attr = attr, label = label):
                    sim_param_values[attr] = False
                    label.setText('False')
                def trueFunc(attr = attr, label = label):
                    sim_param_values[attr] = True
                    label.setText('True')
                btn = QPushButton(self)
                btn.setText('True')
                layout.addWidget(btn, i, 2)
                self.connect(btn,SIGNAL("clicked()"), trueFunc)
                btn = QPushButton(self)
                btn.setText('False')
                layout.addWidget(btn, i, 3)
                self.connect(btn,SIGNAL("clicked()"), falseFunc)
            else:
                label = QLabel(self)
                label.setText(currentStr)
                layout.addWidget(label, i, 1)
                linedit = QLineEdit(self)
                linedit.setText(currentStr)
                layout.addWidget(linedit, i, 2)
                def change(attr = attr, linedit = linedit,
                           paramtype = paramtype, label = label):
                    txt = str(linedit.text())
                    label.setText(txt)
                    if paramtype == STRING:
                        sim_param_values[attr] = txt
                    elif paramtype == INT:
                        if txt.startswith('0x') or txt.startswith('0X'):
                            n = string.atoi(txt[2:], 16)
                        else:
                            n = string.atoi(txt)
                        sim_param_values[attr] = n
                    elif paramtype == FLOAT:
                        sim_param_values[attr] = string.atof(txt)
                btn = QPushButton(self)
                btn.setText('OK')
                layout.addWidget(btn, i, 3)
                self.connect(btn, SIGNAL("clicked()"), change)
        btn = QPushButton(self)
        btn.setText('Done')
        layout.addWidget(btn, len(_sim_param_table), 0, len(_sim_param_table), 4)
        def done(self = self):
            global sim_params_set
            sim_params_set = True
            #import pprint
            #pprint.pprint(sim_param_values)
            self.close()
        self.connect(btn, SIGNAL("clicked()"), done)

_sim_parameter_dialog = None

###################################################
