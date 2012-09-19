# Copyright 2006-2009 Nanorex, Inc.  See LICENSE file for details.
"""
CoNTubGenerator.py - Generator functions which use cad/plugins/CoNTub.

@author: Bruce
@version: $Id$
@copyright: 2006-2009 Nanorex, Inc.  See LICENSE file for details.

Also intended as a prototype of code which could constitute the nE-1 side
of a "generator plugin API". Accordingly, the CoNTub-specific code should
as much as possible be isolated into small parts of this, with most of it
knowing nothing about CoNTub's specific functionality or parameters.
"""

# how to test this: execute this in a debugger:
"""
import commands.InsertHeterojunction.CoNTubGenerator as CoNTubGenerator
reload(CoNTubGenerator)
"""
# Each time you do that, Insert menu gets a new command "Heterojunction". The first one is always the latest one.

import os, sys, time

import foundation.env as env
import utilities.Initialize as Initialize
from utilities.Log import quote_html, redmsg ##, orangemsg, greenmsg
from command_support.ParameterDialog import ParameterDialog, ParameterPane
from command_support.GeneratorController import GeneratorController
from utilities.exception_classes import UserError, PluginBug
from utilities.debug import print_compact_traceback
from platform_dependent.PlatformDependent import find_or_make_any_directory, tempfiles_dir, find_plugin_dir
import utilities.EndUser as EndUser

debug_install = False

def debug_run():
    return False
    # change to env.debug() or a debug pref, someday;
    # also some debug prints we cause in other files don't check this, but they should

### one current bug: menu icon is nondeterministic. guess: need to keep a reference to the iconset that we make for it.
# that seemed to help at first, but it's not enough, bug still happens sometimes when we reload this a lot! ####@@@@

from utilities.debug_prefs import use_property_pane

# ==

def add_insert_menu_item(win, command, name_of_what_to_insert, options = ()): ###e this should be a method of MWsemantics.py
    menuIndex = 2 ### kluge - right after Nanotube, at the moment (since indices start from 0)
    menu = win.buildStructuresMenu
    menutext = "%s" % (name_of_what_to_insert,)
    undo_cmdname = "Insert %s" % (name_of_what_to_insert,) ## get this from caller, or, make it available to the command as it runs
        ###e but need to translate it ourselves, ##qApp.translate("Main Window", "Recent Files", None)
    ## self.connect(self.recentFilePopupMenu, SIGNAL('activated (int)'), self._openRecentFile)
    from widgets.menu_helpers import insert_command_into_menu
    insert_command_into_menu( menu, menutext, command, options = options, position = menuIndex, undo_cmdname = undo_cmdname)
    return

# ==

try:
    output_counter
except:
    output_counter = 0

def parse_arg_pattern(argpat):
    """
    Turn argpat into a list of strings, each a nonempty constant or $param;
    allowed argpat formats are just these three: word, $param.word, $param
    [Someday we might extend this, perhaps even allowing expressions like $dict[$key].]
    """
    # just break it at each '$' or '.'
    assert not '@' in argpat # use this as a marker for splitpoints
        #e (could be \00 in case '@' gets used in a real command line)
    argpat = argpat.replace('$','@$')
    argpat = argpat.replace('.','@.')
    argpat = argpat.split('@')
    if not argpat[0]:
        argpat = argpat[1:]
    assert argpat
    assert argpat == filter(None, argpat), \
           "argpat %r should equal filtered one %r" % (argpat, filter(None, argpat))
            # no other empty strings are legal
    return argpat

def arg_str(arg):
    """
    like str(arg) but suitable for use on a command line
    """
    try:
        ###@@@ horrible temporary kluge for $T item -> value mapping
        res = {"None":0, "Hydrogen": 1, "Nitrogen": 7}[arg]
        arg = res
    except KeyError:
        pass
    return str(arg) ###e stub, probably good enough for contub

class PluginlikeGenerator:
    """
    Superclass for generators whose code is organized similar to that of a (future) plugin.
    Subclasses contain data and methods which approximate the functionality
    of metadata and/or code that would ultimately be found in a plugin directory.
    See the example subclass in this file for details.
    """
    ok_to_install_in_UI = False # changed to True in instances which become ok to install into the UI; see also errorcode
    # default values of subclass-specific class constants
    what_we_generate = "Something"

    # init methods

    def register(subclass): # staticmethod
        win = env.mainwindow()
        try:
            instance = subclass(win)
            if instance.ok_to_install_in_UI:
                instance.install_in_UI()
                if debug_install: print "debug: registered", instance
            else:
                if debug_install: print "debug: didn't register", instance
        except:
            print_compact_traceback("bug in instantiating %r or installing its instance: " % subclass)
        return
    register = staticmethod(register)

    errorcode = 0
        # this gets set to something true (by self.fatal) if an error occurs which should
        # permanently disable this plugin (during setup or use)
    errortext = ""
        # this gets set to errortext for the first error that permanently disabled this plugin

    def fatal(self, errortext, errorcode = 1):
        """
        Our submethods call this to report a fatal setup/use error; it prints errortext appropriately
        and sets self.errorcode and self.errortext.
        """
        if not errorcode:
            print "bug: fatal errorcode must be a boolean-true value, not %r" % (errorcode,)
            errorcode = 1
        if self.errorcode:
            print "plugin %r bug: self.errorcode was already set before fatal was called" % (self.plugin_name,)
        if not self.errorcode or not self.errortext:
            self.errortext = errortext # permanent record for use by callers
        self.errorcode = errorcode
        msg = "plugin %r fatal error: %s" % (self.plugin_name, errortext,)
        print msg
        env.history.message(redmsg(quote_html(msg))) # it might be too early for this to be seen
        return errorcode

    def __init__(self, win):
        self.win = win

        # All these submethods should call self.fatal to report permanent fatal errors.
        # And after calling the ones that can, we should check self.errorcode before continuing.

        # Find plugin dir -- if we can't, it has to be a fatal error,
        # since (once this is using a real plugin API) we won't have the metadata
        # needed to install the plugin in the UI.

        path = self.find_plugin_dir()
        if self.errorcode:
            return
        self.plugin_dir = path # for error messages, and used by runtime methods

        # make sure the stuff we need is in the plugin dir (and try to use it to set up the dialogs, commands, etc)
        self.setup_from_plugin_dir() # this prints error msgs if it needs to
        if self.errorcode:
            return

        # don't create a working directory until the plugin is first used
        # (since we don't want to create one at all, if it's not used in the session,
        #  since they might be created in a session-specific place)
        self.working_directory = None

        if debug_install: print "plugin init is permitting ok_to_install_in_UI = True"
        self.ok_to_install_in_UI = True
        return

    def find_plugin_dir(self):
        ok, path = find_plugin_dir(self.plugin_name)
        if ok:
            assert os.path.isdir(path)
            return path
        else:
            errortext = path
            self.fatal( errortext)
            return None
        pass

    def setup_from_plugin_dir(self):
        """
        Using self.plugin_dir, setup dialogs, commands, etc. Report errors to self.fatal as usual.
        """
        # The following will someday read metainfo from the plugin.desc file,
        # but for now we just grab that info from constants set by the subclass
        # (the subclass which won't exist when this is a real public plugin API).

        # param desc file (must exist)
        param_desc_path = os.path.join(self.plugin_dir, self.parameter_set_filename)
        self.param_desc_path = param_desc_path
        if not os.path.isfile(param_desc_path):
            return self.fatal("can't find param description file [%s]" % (param_desc_path,))
        # executable (find its path, make sure it exists)
        self.executable # should be provided by subclass
        if sys.platform == 'win32':
            executable_names = [self.executable + ".exe", self.executable] # Windows: try both, in this order
        else:
            executable_names = [self.executable] # Linux or Mac: only try plain name
        self.executable_path = None
        for tryname in executable_names:
            executable_path = os.path.join(self.plugin_dir, "bin", tryname)
            if os.path.exists(executable_path):
                # assume if it exists at all, it's the command we want
                # (it might be a file or a symlink, and I'm not sure if isfile works across symlinks;
                #  if it does, we'd want to use isfile here, and warn if exists but not isfile #k)
                self.executable_path = executable_path
                if debug_install: print "plugin exec path = %r" % (executable_path,)
                break
            continue
        if not self.executable_path:
            return self.fatal("can't find executable; looked for %s" % (executable_names,))

        self.setup_commandline_info() # this is far below, just before the code that uses what it computes

        ###e maybe get the param set, create the dialog, etc
        # (even run a self test if it defines one? or wait 'til first used?)
        return

    whatsThisText = """<u><b>Insert Heterojunction</b></u>
    <p>A heterojunction is a joint connecting two carbon nanotubes which may differ in radius
    and chirality. The joint is made of sp<sup>2</sup>-hybridized carbon atoms, arranged in
    hexagons and pentagons (the pentagons allow for curvature of the surface) to join the two
    nanotubes with the same material they are composed of.</p>
    <p>This is Nanorex\'s modified version of the CoNTub source code written
    by S. Melchor and J. Dobado at the Universidad de Granada in Spain.
    Citations of this work should be formatted as follows:<p>
    <blockquote>"CoNTub: an algorithm for connecting two arbitrary carbon
    nanotubes." S. Melchor; J.A. Dobado. Journal of Chemical Information
    and Computer Sciences, 44, 1639-1646 (2004)</blockquote>
    <p>Nanorex\'s modifications include translation from Java to C++,
    performance improvement in bond inference, changing the output file
    format from pdb to mmp, and revising the stderr messages and exit code.
    </p>"""

    def install_in_UI(self):
        """
        Create a menu command, or whatever other UI elements should invoke the plugin's generator.
        Report errors to self.fatal as usual.
        """
        assert self.ok_to_install_in_UI
        #e create whatever we want to be persistent which was not already done in setup_from_plugin_dir (nothing yet?)

        #e install the necessary commands in the UI (eg in insert menu)
        ### WRONG -- menu text should not contain Insert, but undo cmdname should (so separate option is needed), and needs icon
        ###e add options for things like tooltip text, whatsthis text, iconset
        icon_path = self.find_title_icon()
        options = [('iconset', icon_path), ('whatsThis', self.whatsThisText)]
        self.menu_item_id = add_insert_menu_item( self.win, self.command_for_insert_menu, self.what_we_generate, options)
        ###e make that a menu item controller, and give it a method to disable the menu item, and do that on error(??) ###@@@
        pass

    def find_title_icon(self):
        icon_path = os.path.join(self.plugin_dir, "images/HJ_icon.png") #######@@@@@@@ KLUGE - hardcode this relpath for now
        ###@@@ need to get icon name from one of the desc files (not positive which one, probably params but if there is one
        # for the overall "single generator command" then from that one), interpret it using an icon path, and then feed it
        # not only to this menu item, but to the generated dialog as well. this code to find it will be in setup_from_plugin_dir
        # I think. or maybe (also) called again each time we make the dialog?
        if not os.path.isfile(icon_path):
            print "didn't find [%s], using modeltree/junk.png" % icon_path
            icon_path = "modeltree/junk.png"
        # icon_path will be found later by imagename_to_pixmap I think; does it work with an abspath too?? #####@@@@@
        return icon_path

    # runtime methods

    def create_working_directory_if_needed(self):
        """
        If it hasn't been done already, create a temporary directory (fixed pathname per plugin per session)
        for this plugin to use. Report errors to self.fatal as usual.
        """
        if self.working_directory:
            return
        subdir = os.path.join( tempfiles_dir(), "plugin-" + self.plugin_name )
        errorcode, path = find_or_make_any_directory(subdir)
        if errorcode:
            # should never happen, but make sure caller checks self.errorcode (set by fatal) just in case #####@@@@@
            errortext = path
            return self.fatal(errortext)
        self.working_directory = subdir
        return

    dialog = None
    param_desc_path_modtime = None

    def make_dialog_if_needed(self):
        """
        Create self.dialog if necessary.
        """
        # For developers, remake the dialog from its description file each time that file changes.
        # (The point of only remaking it then is not speed, but to test the code when it doesn't get remade,
        #  since that's what always happens for non-developers.)
        # (Someday, when remaking it, copy its window geometry from the old one. Then put that code into the MMKit too. ###e)
        # For others, only make it the first time.

        if (EndUser.enableDeveloperFeatures() or env.debug()) and self.dialog:
            # For developers, remake the dialog if its description file changed (by zapping the old dialog here).
            zapit = False
            modtime = os.stat(self.param_desc_path).st_mtime
            if modtime != self.param_desc_path_modtime:
                zapit = True
                self.param_desc_path_modtime = modtime
            if zapit:
                #e save geometry?
                self.dialog.hide()
                self.dialog.destroy() ###k
                self.dialog = None
            pass
        if not self.dialog:
            if debug_run():
                print "making dialog from", self.parameter_set_filename
            dialog_env = self
                # KLUGE... it needs to be something with an imagename_to_pixmap function that knows our icon_path.
                # the easiest way to make one is self... in future we want our own env, and to modify it by inserting that path...
            if use_property_pane():
                # experimental, doesn't yet work [060623]
                parent = self.win.vsplitter2 ###@@@ could this parent be wrong? it acted like parent was self.win or so.
                clas = ParameterPane ###@@@ worked internally, buttons printed debug msgs, but didn't have any effects in GBC.
            else:
                # usual case
                parent = self.win
                clas = ParameterDialog
            self.dialog = clas( self.win, self.param_desc_path, env = dialog_env )
                # this parses the description file and makes the dialog,
                # but does not show it and does not connect a controller to it.
            #e set its geometry if that was saved (from above code or maybe in prefs db)
        return

    def imagename_to_pixmap(self, imagename): # KLUGE, see comment where dialog_env is set to self ###@@@ might work but untested ###@@@
        from utilities.icon_utilities import imagename_to_pixmap
        path = None
        for trydir in [self.plugin_dir, os.path.join(self.plugin_dir, "images")]:
            trypath = os.path.join( trydir, imagename )
            if os.path.isfile(trypath):
                # assume it's the one we want
                path = trypath
                break
        if not path:
            path = imagename # use relative name
        return imagename_to_pixmap(path)

    def command_for_insert_menu(self):
        """
        Run an Insert Whatever menu command to let the user generate things using this plugin.
        """
        if self.errorcode:
            env.history.message(redmsg("Plugin %r is permanently disabled due to this error, reported previously: %s" % \
                               (self.plugin_name, self.errortext)))
            return
        self.create_working_directory_if_needed()
        assert not self.errorcode
        if debug_run():
            print 'ought to insert a', self.what_we_generate
        self.make_dialog_if_needed()
        dialog = self.dialog
        ###e Not yet properly handled: retaining default values from last time it was used. (Should pass dict of them to the maker.)
        dialog.set_defaults({}) ### IMPLEM
        controller = GeneratorController(self.win, dialog, self)
            # Note: this needs both self and the dialog, to be inited.
            # So it takes care of telling the dialog to control it (and not some prior controller).
        dialog.show()
        # now it's able to take commands and run its callbacks; that does not happen inside this method, though, does it?
        # hmm, good question... if it's modal, this makes things easier (re preview and bug protection)...
        # and it means the undo wrapping was ok... but what do we do here to make it modal?
        # 1. find out by test if other generators are modal.
        # 2. find out from code, how.

        pass###e

    def build_struct(self, name, params, position):
        """
        Same API as in GeneratorBaseClass (though we are not its subclass).
        On error, raise an exception.
        """
        # get executable, append exe, ensure it exists
        program = self.executable_path
        # make command line args from params
        args, outfiles = self.command_line_args_and_outfiles(params, name)
            # makes param args and outputfile args;
            # args is a list of strings (including outfile names);
            # outfiles is a list of full pathnames of files this command might create
        # run executable using the way we run the sim
        exitcode = self.run_command(program, args)
        #e look at exitcode?
        if exitcode and debug_run():
            print "generator exitcode: %r" % (exitcode,)
        if exitcode:
            # treat this as a fatal error for this run [to test, use an invalid chirality with m > n]
            msg = "Plugin %r exitcode: %r" % (self.plugin_name, exitcode)
            ## not needed, GBC UserError will do it, more or less: env.history.message(redmsg(msg))
            ###e should: self.remove_outfiles(outfiles, complain_if_missing = False)
            raise UserError(msg) # this prints a redmsg; maybe we'd rather do that ourselves, and raise SilentUserError (nim)??
        # look for outfiles
        # (if there are more than one specified, for now just assume all of them need to be there)
        for outfile in outfiles:
            if not os.path.exists(outfile):
                ###e should: self.remove_outfiles(outfiles, complain_if_missing = False)
                raise PluginBug( "generator output file should exist but doesn't: [%s]" % (outfile,) )
        # insert file contents, rename the object in it, return that (see dna generator)
        thing = self.insert_output(outfiles, params, name)
            # we pass params, since some params might affect insertion (or postprocessing)
            # other than by affecting the command output
        ###@@@ WARNING: the following repositioning code is not correct for all kinds of "things",
        # only for single-chunk things like for CoNTub
        # (and also it probably belongs inside insert_output, not here):
        for atom in thing.atoms.values():
            atom.setposn(atom.posn() + position)
        self.remove_outfiles(outfiles)
        return thing

    def setup_commandline_info(self):
        """
        #doc
        [This is run at setup time, but we put this method here
        since the arg data it compiles (into a nonobvious internal format)
        is used to make the command lines at runtime, in the methods just below.]
        """
        # command-line, output file info
        # examples:
        ## outputfiles_pattern = "$out1.mmp"
        ## executable_args_pattern = "$n1 $m1 $L1 $n2 $m2 $L2 $T 1 $out1.mmp"

        self.outputfiles_pattern # make sure subclass defines these
        self.executable_args_pattern

        self.outfile_pats = map( parse_arg_pattern, self.outputfiles_pattern.split())
        self.cmdline_pats = map( parse_arg_pattern, self.executable_args_pattern.split())

        if debug_install:
            print "got these parsed argpats: %r\nand outfiles: %r" % (self.cmdline_pats, self.outfile_pats)

        self.paramnames_dict = {} # for now, maps pn -> $pn
        self.outfile_paramname_extension_pairs = []
            # one or more pairs of ($paramname_for_filebasename, extension), e.g. [('$out1', '.mmp')]
        self.paramnames_order = []
            # needed for defining order of tuples from gather_parameters; leave out outfile params;
            # this attr will be used directly by our GeneratorController

        for pat in self.outfile_pats:
            assert len(pat) <= 2 # ok if no extension, at least for now
            try:
                baseparam, ext = pat
            except:
                baseparam, ext = pat, ''
            assert baseparam.startswith('$')
            assert not ext or ext.startswith('.')
            self.outfile_paramname_extension_pairs.append(( baseparam, ext )) ### leave in '$' -- useful to look up val

        self.outfile_paramnames = [pn[1:] for (pn, ext) in self.outfile_paramname_extension_pairs]

        for pat in self.cmdline_pats:
            for word in pat:
                if word.startswith('$'):
                    name = word[1:]
                    if name not in self.paramnames_dict:
                        self.paramnames_dict[name] = word # so it maps x -> $x
                        if name not in self.outfile_paramnames:
                            self.paramnames_order.append(name)
                    pass
                continue
            continue

        assert self.paramnames_dict
        assert self.paramnames_order
        assert self.outfile_paramname_extension_pairs

        if debug_install:
            print "outfile_paramname_extension_pairs:", self.outfile_paramname_extension_pairs
            print "paramnames_dict", self.paramnames_dict
            print "outfile_paramnames", self.outfile_paramnames
            print "paramnames_order", self.paramnames_order

        # see command_line_args_and_outfiles() for how all this is used
        return

    def command_line_args_and_outfiles(self, params, name):
        """
        Given the parameter-value tuple (same order as self.paramnames_order),
        and the desired name of the generated structure in the MT (optional to use it here
         since insert code will also impose it),
        return a list of command line args, and a list of output files, for use in one command run.
        """
        workdir = self.working_directory
        outfiles = []
        args = []
        paramvals = {} # $pn -> value for subst
        for pn, val in zip(self.paramnames_order, params):
            paramvals['$' + pn] = val
        for (pn, ext) in self.outfile_paramname_extension_pairs:
            # pn is like $out1, ext is empty or like .mmp, and only some exts are supported but that's up to insert method
            global output_counter
            output_counter += 1
            basename = 'output%d' % output_counter #e improve? make it be the same if we preview?? (how? GBC AP doesn't tell us!)
            path = os.path.join( workdir, basename + ext)
            outfiles.append( path)
            assert pn not in paramvals
            paramvals[pn] = os.path.join( workdir, basename) # leave ext off of this, since cmdline pattern adds it back
        for argpat in self.cmdline_pats:
            arg = ""
            for word in argpat:
                if word.startswith('$'):
                    arg += arg_str(paramvals[word])
                else:
                    arg += word
            assert arg
            args.append(arg)
        return args, outfiles

    def run_command(self, program, args):
        if debug_run():
            print "will run this command:", program, args
        from PyQt4.Qt import QStringList, QProcess, QObject, SIGNAL, QDir
        # modified from runSim.py
        arguments = QStringList()
        if sys.platform == 'win32':
            program = "\"%s\"" % program # Double quotes needed by Windows. ###@@@ test this
        ### try it with blanks in output file name and in program name, once it works ###@@@
        for arg in [program] + args:
            if arg:
                arguments.append(arg)
        self.simProcess = simProcess = QProcess()
        simProcess.setArguments(arguments)
        simProcess.setWorkingDirectory(QDir(self.working_directory)) # in case it writes random files
        if 1:
            # report stdout/stderr
            def blabout():
                print "stdout:", simProcess.readStdout()
                ##e should also mention its existence in history, but don't copy it all there in case a lot
            def blaberr():
                text = str(simProcess.readStderr()) # str since it's QString (i hope it can't be unicode)
                print "stderr:", text
                env.history.message(redmsg("%s stderr: " % self.plugin_name + quote_html(text)))
                # examples from CoNTub/bin/HJ:
                # stderr: BAD INPUT
                # stderr: Error: Indices of both tubes coincide
            QObject.connect(simProcess, SIGNAL("readyReadStdout()"), blabout)
            QObject.connect(simProcess, SIGNAL("readyReadStderr()"), blaberr)
        started = simProcess.start() ###k what is this code? i forget if true means ok or error
        if debug_run():
            print "qprocess started:",started
        while 1:
            ###e need to make it abortable! from which abort button? ideally, one on the dialog; maybe cancel button??
            # on exception: simProcess.kill()
            if simProcess.isRunning():
                if debug_run():
                    print "still running"
                    time.sleep(1)
                else:
                    time.sleep(0.1)
            else:
                break
        if debug_run():
            print "process done i guess: normalExit = %r, (if normal) exitStatus = %r" % \
                  (simProcess.normalExit(), simProcess.exitStatus())
        if 1:
            QObject.disconnect(simProcess, SIGNAL("readyReadStdout()"), blabout)
            QObject.disconnect(simProcess, SIGNAL("readyReadStderr()"), blaberr)
        if simProcess.normalExit():
            return simProcess.exitStatus()
        else:
            return -1

    def insert_output(self, outfiles, params, name):
        ## return self.create_methane_test(params, name)
        if debug_run():
            print "inserting output from",outfiles ###@@@
        # modified from dna generator's local function insertmmp(filename, tfm)
        assert len(outfiles) == 1 # for now
        filename = outfiles[0]
        assert filename.endswith('.mmp') # for now; in future, also permit .pdb or anything else we know how to read
        assy = self.win.assy #k
        from files.mmp.files_mmp import readmmp
        ok_junk, grouplist  = readmmp(assy, filename, isInsert = True)
            # WARNING: ok_junk is not a boolean; see readmmp doc for details
        if not grouplist:
            raise Exception("Trouble with output file: " + filename)###@@@ predict NameError: Exception (good enough for now)
        viewdata, mainpart, shelf = grouplist
        if len(mainpart.members) == 1:
            thing = mainpart.members[0]
        else:
            thing = mainpart # won't happen for now
        del viewdata #k or kill?
        thing.name = name
        shelf.kill()
        # wware 060704 - fix valence problems on the ends
        while True:
            found_one = False
            for atm in thing.atoms.values():
                if atm.element.symbol == 'C' and len(atm.realNeighbors()) == 1:
                    atm.kill()
                    found_one = True
            if not found_one:
                break
        for atm in thing.atoms.values():
            if atm.element.symbol == 'C' and len(atm.realNeighbors()) == 2:
                atm.set_atomtype('sp2', always_remake_bondpoints = True)
        # problem: for some kinds of errors, the only indication is that we're inserting a 0-atom mol, not a many-atom mol. hmm.
        ####@@@@
        return thing # doesn't actually insert it, GBC does that

    def remove_outfiles(self, outfiles):
        print "removing these files is nim:", outfiles ###@@@

    def create_methane_test(self, params, name):
        # example: build some methanes
        print "create_methane_test"
        assy = self.win.assy
        from geometry.VQT import V
        from model.chunk import Chunk
        from model.chem import Atom
        mol = Chunk(assy, 'bug') # name is reset below!
        n = max(params[0],1)
        for x in range(n):
          for y in range(2):
            ## build methane, much like make_Atom_and_bondpoints method does it
            pos = V(x,y,0)
            atm = Atom('C', pos, mol)
            atm.make_bondpoints_when_no_bonds() # notices atomtype
        mol.name = name
        ## assy.addmol(mol)
        return mol

    pass # end of class PluginlikeGenerator

class HeterojunctionGenerator(PluginlikeGenerator):
    """
    Encapsulate the plugin-specific data and code (or references to it)
    for the CoNTub plugin's heterojunction command.
       In a real plugin API, this data would come from the plugin directory,
    and this code would be equivalent to either code in nE-1 parameterized by metadata in the plugin directory,
    and/or actual code in the plugin directory.
       (The present example is clearly simple enough to be the contents of a metadata file,
    but not all of the other built-in generators are that simple.)
    """
    topic = 'CoNTub' # for sponsor_keyword for GeneratorBaseClass's SponsorableMixin superclass (and for submenu?)
    what_we_generate = "Heterojunction"
        # used for insert menu item text, undo cmdname, history messages, new node names; not sure about wikihelp featurename
    menu_item_icon = "blablabla"
    plugin_name = "CoNTub"
        # used as directory name, looked for in ~/Nanorex/Plugins someday, and in cad/plugins now and someday...
    parameter_set_filename = "HJ-params.desc"
    executable = "HJ" # no .exe, we'll add that if necessary on Windows ## this might not be required of every class
    outputfiles_pattern = "$out1.mmp"
    executable_args_pattern = "$n1 $m1 $L1 $n2 $m2 $L2 $T 1 $out1.mmp"

    pass # end of class HeterojunctionGenerator

def initialize():
    # must be called after mainwindow exists
    if (Initialize.startInitialization(__name__)):
        return
    PluginlikeGenerator.register(HeterojunctionGenerator)
    Initialize.endInitialization(__name__)

# end
