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

from foundation.FeatureDescriptor import find_or_make_descriptor_for_possible_feature_object
from foundation.FeatureDescriptor import command_package_part_of_module_name
from foundation.FeatureDescriptor import otherCommandPackage_Descriptor

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
        print
        
    except:
        print_compact_traceback("ignoring exception: ")
        
    os.chdir(_original_cwd)
    
    return # from import_all_modules_cmd

# ==

def export_command_table_cmd(glpane, _might_reload = True): #bruce 080721, unfinished
    """
    @note: since this only covers loaded commands, you might want to
           run "Import all source files" before running this.
    """
    if _might_reload:
        try:
            import operations.ops_debug as _this_module
                # (to be precise: new version of this module)
            reload(_this_module)
            _this_module.export_command_table_cmd # make sure it's there
        except:
            print_compact_traceback("fyi: auto-reload failed: ")
            pass
        else:
            _this_module.export_command_table_cmd(glpane, _might_reload = False)
            return
        pass
    
    del glpane

    global_values = {} # id(val) -> val (not all vals are hashable)
    mcount = 0

    all_command_packages_dict = {}

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
            if 0:
                print module # e.g. <module 'commands.Move' from '/Nanorex/trunk/cad/src/commands/Move/__init__.pyc'>
                print getattr(module, '__file__', '<no file>') # e.g. /Nanorex/trunk/cad/src/commands/Move/__init__.pyc
                    # e.g. <module 'imp' (built-in)> has no file; name is 'imp'
                print getattr(module, '__name__', '<no name>') # e.g. commands.Move
                    # all modules have a name.
                print
            cp = command_package_part_of_module_name( module.__name__)
            if cp:
                all_command_packages_dict[ cp] = cp
            pass
        continue

    print "found %d distinct global values in %d modules" % ( len(global_values), mcount)

    print "found %d command_packages" % len(all_command_packages_dict) # a dict, from and to their names
    all_command_packages_list = all_command_packages_dict.values()
    all_command_packages_list.sort()
    
    # print "\n".join( all_command_packages_list)
    # print

    if 1:
        # not needed, just curious how many types there are
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

    # find command descriptors in global_values
    descriptors = {}
    for thing in global_values.itervalues():
        d = find_or_make_descriptor_for_possible_feature_object( thing)
        if d is not None:
            descriptors[d] = d # duplicates can occur

    # add notes about the command packages in which we didn't find any commands,
    # and warn about those in which we found more than one
    command_packages_with_commands = {}
    for d in descriptors:
        cp = d.command_package
        if cp:
            if cp not in all_command_packages_dict:
                print "bug: command package not found in initial scan:", cp
            if command_packages_with_commands.has_key(cp):
                print "warning: command package with more than one command:", cp
            command_packages_with_commands[ cp] = cp

    for cp in all_command_packages_list:
        if not cp in command_packages_with_commands:
            d = otherCommandPackage_Descriptor(cp)
            descriptors[d] = d
    
    # change descriptors into a list, and sort it
    items = [ ( descriptor.sort_key(), descriptor) for descriptor in descriptors]
        ### or call sort_by or sorted_by, if it exists?
    items.sort()
    descriptors = [ descriptor for junk, descriptor in items ]

    # print results
    
    print "found %d commands:" % len(descriptors)
    print

    for descriptor in descriptors:
        descriptor.print_plain() # todo: add more info to that; print into a file
        print
    
    print "done"

    return # from export_command_table_cmd

# ==

def initialize(): # called from startup_misc.py
    if EndUser.enableDeveloperFeatures():
        register_debug_menu_command( "Import all source files", import_all_modules_cmd )
        register_debug_menu_command( "Export command table", export_command_table_cmd )
    return

# end
