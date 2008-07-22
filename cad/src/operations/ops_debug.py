# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
ops_debug.py -- various operations/commands for debugging

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""

import sys, os
import utilities.EndUser as EndUser
from utilities.constants import CAD_SRC_PATH
from utilities.debug import print_compact_traceback
from utilities.debug import register_debug_menu_command
from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir

# ==

def _tempfilename( basename): # todo: rename, refile
    """
    @warning: does not check whether file already exists.
    """
    tmpdir = find_or_make_Nanorex_subdir("TemporaryFiles") # also hardcoded elsewhere
    return os.path.join( tmpdir, basename )

# ==

def import_all_modules_cmd(glpane): #bruce 080721
    """
    """
    del glpane
    
    _original_cwd = os.getcwd() # so we can restore it before returning
    
    try:
        os.chdir(CAD_SRC_PATH)
        
        # this doesn't work, don't know why:
        ## pipe = os.popen("./tools/AllPyFiles.sh")
        ## modules = pipe.readlines() # IOError: [Errno 4] Interrupted system call
        ## pipe.close()
        
        # so try this instead:
        tmpfile = _tempfilename( "_all_modules")
        os.system("./tools/AllPyFiles.sh > '%s'" % tmpfile)
        file1 = file(tmpfile, "rU")
        modules = file1.readlines()
        file1.close
        os.remove(tmpfile)
        
        print "will scan %d source files from AllPyFiles" % len(modules) # 722 files as of 080721!

        modules.sort()

        SKIP_THESE = ("_import_roots", "main", "ExecSubDir")

        import_these = []
        cinit = 0
        
        for module in modules:
            module = module.strip()
            if module.startswith("./"):
                module = module[2:]
            basename = module
            assert os.path.exists(module), "should exist: %r" % (module,)
            assert module.endswith(".py"), "should end with .py: %r" % (module,)
            module = module[:-3]
            if module.endswith("/__init__"):
                # don't bother with this if its directory is empty;
                # otherwise assume it'll be imported implicitly
                cinit += 1
                continue
            if module in SKIP_THESE or ' ' in module or '-' in module:
                # those funny chars can happen when developers have junk files lying around
                # todo: do a real regexp match, permit identifiers and '/' only;
                # or, only do this for files known to svn?
                print "skipping import of", basename
                continue
            import_these.append(module.replace('/', '.'))
            continue
        if cinit:
            print "(skipping direct import of %d __init__.py files)" % cinit
        print

        print "will import %d modules" % len(import_these)

        for module in import_these:
            statement = "import " + module
            try:
                exec statement
            except:
                print_compact_traceback("ignoring exception in %r: " % statement)
                pass

        print "done importing all modules"
        
    except:
        print_compact_traceback("ignoring exception: ")
        
    os.chdir(_original_cwd)
    
    return # from import_all_modules_cmd

# ==

def export_command_table_cmd(glpane): #bruce 080721, unfinished
    """
    @note: since this only covers loaded commands, you might want to
           run "Import all source files" before running this.
    """
    del glpane

    global_values = {} # id(val) -> val (not all vals are hashable)
    mcount = 0

    for module in sys.modules.itervalues():
        if module:
            # Note: this includes built-in and extension modules.
            # If they were easy to exclude, we'd exclude them here,
            # since we are only looking for objects defined in modules
            # in cad/src. I guess comparing __file__ and CAD_SRC_PATH
            # would not be too hard... so do that if the need arises.
            mcount += 1
            for name in dir(module):
                value = getattr(module, name)
                global_values[id(value)] = value # also store module and name?

    print "found %d distinct global values in %d modules" % ( len(global_values), mcount)

    if 1:
        # not needed, just curious
        global_value_types = {} # maps type -> type (I assume all types are hashable)
        for v in global_values.itervalues():
            t = type(v)
            global_value_types[t] = t
        print "of %d distinct types" % len(global_value_types)
            # 745 types!
            # e.g. one class per OpenGL function, for some reason;
            # and some distinct types which print the same,
            # e.g. many instances of <class 'ctypes.CFunctionType'>.

        # print global_value_types.values() # just to see it...
        print

    # now look for Python classes of certain kinds.
    # note that issubclass has an exception for a non-class.

    # TODO: replace this with a registration scheme:

    from command_support.Command import basicCommand
    CLASSES = (basicCommand, ) # needs to be a tuple, not a list, for issubclass 2nd arg

    commands = [] # commands
    
    for val in global_values.itervalues():
        try:
            if issubclass(val, CLASSES):
                commands.append(val)
        except:
            pass # issubclass has exception for non-class

    print "found %d commands:" % len(commands)
    print
    
    printlines = ['%r' % command for command in commands]
    printlines.sort()
    
    print '\n'.join(printlines)
    print
    print "done (mostly nim)"

    return # from export_command_table_cmd

# ==

def initialize(): # called from startup_misc.py
    if EndUser.enableDeveloperFeatures():
        register_debug_menu_command( "Import all source files", import_all_modules_cmd )
        register_debug_menu_command( "Export command table", export_command_table_cmd )
    return

# end
