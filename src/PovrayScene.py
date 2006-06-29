# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
PovrayScene.py - The POV-Ray Scene class.

$Id$

History:

mark 060601 - Created.

'''

__author__ = "Mark"

from Utility import SimpleCopyMixin, Node, imagename_to_pixmap
from povray import write_povray_ini_file, launch_povray_or_megapov
from fileIO import writepovfile
from qt import Qt, QApplication, QCursor
from HistoryWidget import greenmsg, redmsg
import env, os, sys
from platform import find_or_make_any_directory, find_or_make_Nanorex_subdir

PVSNum = 0
def genPVSNum(string):
    """return string appended with a unique POV-Ray Scene number"""
    global PVSNum
    PVSNum += 1
    return string + str(PVSNum)

class PovrayScene(SimpleCopyMixin, Node):
    """A POV-Ray Scene is a .pov file that can be used to render images, accessible from the Model Tree as a node.
    """

    sym = "POV-Ray Scene"
    extension = ".pov"
    povrayscene_file = '' #&&& This is the absolute path to the povray scene file. This needs to be the relative path.

    width = height = output_type = None #bruce 060620, might not be needed
    
    copyable_attrs = Node.copyable_attrs + ('width', 'height', 'output_type', 'povrayscene_file')
        #&&& This doesn't work. Does it have something to do with <povrayscene_file> missing from set_parameters?
        #&&& Ask Bruce. Mark 060613.
        # No, it's because _um_initargs (inherited from Node) is not compatible with the args to our __init__ method.
        # I'll fix the __init__ method instead of overriding _um_initargs, since that way it's compatible with
        # the __init__ methods of other nodes, which makes client code clearer. [bruce 060620]

    def __init__(self, assy, name, params = None):
        #bruce 060620 removed name from params list, made that optional, made name a separate argument,
        # all to make this __init__ method compatible with that of other nodes (see above for one reason);
        # also revised this routine in other ways, e.g. to avoid redundant sets of self.assy and self.name
        # (which are set by Node.__init__).
        if not name: 
            # Name is only generated here when called by "View > Raytrace Scene": ops_view.viewRaytraceScene().
            # [Note: this code might be superceded by code in Node.__init__ once nodename suffix numbers are revised.]
            name = genPVSNum("%s-" % self.sym) + self.extension
##        self.assy = assy -- this is done by Node.__init__, no need to do it here
        Node.__init__(self, assy, name)
        if params:
            self.set_parameters(params)
        self.const_icon = imagename_to_pixmap("povrayscene.png")
            # note: this might be changed later; this value is not always correct; that may be a bug when this node is copied.
            # [bruce 060620 comment]
        return
        
    def set_parameters(self, params): #bruce 060620 removed name from params list
        '''Sets all parameters in the list <params> for this POV-Ray Scene.
        '''
        self.width, self.height, self.output_type = params
        self.assy.changed()
        
    def get_parameters(self): #bruce 060620 removed name from params list
        '''Returns list of parameters for this POV-Ray Scene.
        '''
        return (self.width, self.height, self.output_type)

    def edit(self):
        "Opens POV-Ray Scene properties dialog with current parameters."
        self.assy.w.povrayscenecntl.setup(self)
        
    def writemmp(self, mapping):
        mapping.write("povrayscene (" + mapping.encode_name(self.name) + ") %d %d %s\n" % \
            (self.width, self.height, self.output_type))
        
        # Write absolute path of POV-Ray Scene file into info record.
        # Get the basename from the povrayscene_file since there is no guarantee that the name and the basename are
        # still the same, since the user could have renamed the node and this does not change the povrayscene filename.
        dir, basename = os.path.split(self.povrayscene_file)
        mapping.write("info povrayscene povrayscene_file = POV-Ray Scene Files/%s\n" % basename) # Relative path.
        # This is still flimsy since it assumes <basename> exists in the POV-Ray Scene Files directory.
        # This is OK for now since it will be true a majority of the time, except for the frequent situation mentioned below.
        #&&& Problem: Users will assume when they rename an existing MMP file, all the POV-Ray Scene files will still be associated 
        #&&& with the MMP file when in fact they will not be. Bruce and I discussed the idea of copying the Part Files directory and
        #&&& its contents when renaming an MMP file. This is an important issue to resolve since it will happen frequently. Mark 060625.
        
        self.writemmp_info_leaf(mapping)
        return
    
    def readmmp_info_povrayscene_setitem( self, key, val, interp ):
        """This is called when reading an mmp file, for each "info povrayscene" record
        which occurs right after this node is read and no other (povrayscene) node has been read.
           Key is a list of words, val a string; the entire record format
        is presently [060108] "info povrayscene <key> = <val>", and there is exactly
        one word in <key>, "povrayscene_file". <val> is the povrayscene filename.
        <interp> is not currently used.
        """
        if len(key) != 1:
            if platform.atom_debug:
                print "atom_debug: fyi: info povrayscene with unrecognized key %r (not an error)" % (key,)
            return
        if key[0] == 'povrayscene_file':
            if val:
                if val[0] == '/' or val[0] == '\\':
                    # val is an absolute path.
                    self.povrayscene_file = val 
                else:
                     # val is a relative path. Build the absolute path.
                    errorcode, dir = self.assy.find_or_make_part_files_directory()
                    self.povrayscene_file = os.path.normpath(os.path.join(dir, val))
                self.update_icon( print_missing_file = True)
            pass
        return

    def update_icon(self, print_missing_file = False, found = None):
        """Update our icon according to whether our file exists or not (or use the boolean passed as found, if one is passed).
        (Exception: icon looks normal if filename is not set yet.
         Otherwise it looks normal if file is there, not normal if file is missing.)
        If print_missing_file is true, print an error message if the filename is non-null but the file doesn't exist.
        Return "not found" in case callers want to print their own error messages (for example, if they use a different filename).
        """
        #bruce 060620 split this out of readmmp_info_povrayscene_setitem for later use in copy_fixup_at_end (not yet done ###@@@). 
        # But its dual function is a mess (some callers use their own filename) so it needs more cleanup. #e
        filename = self.povrayscene_file
        if found is None:
            found = not filename or os.path.exists(filename)
        # otherwise found should have been passed as True or False
        if found:
            self.const_icon = imagename_to_pixmap("povrayscene.png")
        else:
            self.const_icon = imagename_to_pixmap("povrayscene-notfound.png")
            if print_missing_file:
                msg = redmsg("POV-Ray Scene file [" + filename + "] does not exist.") #e some callers would prefer orangemsg, cmd, etc.
                env.history.message(msg)
        return not found
        
    def __str__(self):
        return "<povrayscene " + self.name + ">"
    
    def write_povrayscene_file(self):
        '''Writes a POV-Ray Scene file of the current scene in the GLPane to the POV-Ray Scene Files directory.
        If successful, returns errorcode=0 and the absolute path of povrayscene file.
        Otherwise, returns errorcode=1 with text describing the problem writing the file.
        '''
        ini, pov = self.get_povfile_pair() # pov includes the POV-Ray Scene Files directory in its path.
        if not ini:
            return 1, "Can't get POV-Ray Scene filename"
        #print "write_povrayscene_file(): povrayscene_file=", pov
        writepovfile(self.assy.part, self.assy.o, pov)
        return 0, pov
    
    def get_povfile_pair(self, tmpfile = False):
        """Returns the POV-Ray INI filename and its POV-Ray Scene filename pair. 
        If there was any problem, returns None.
        """
    
        # The ini and pov files must exist in the same directory due to POV-Ray's I/O Restriction feature. Mark 060625.
    
        ini_filename = "povray.ini"
        # Critically important: POV-Ray uses the INI filename as an argument; it cannot have any whitespaces.
        # This is a POV-Ray bug on Windows only. For more information about this problem, see:
        # http://news.povray.org/povray.windows/thread/%3C3e28a17f%40news.povray.org%3E/?ttop=227783&toff=150
        # Mark 060624.
    
        if tmpfile:
            pov_filename = "povrayscene.pov"
            from platform import find_or_make_Nanorex_subdir
            dir = find_or_make_Nanorex_subdir("POV-Ray")
            if not dir:
                return None, None
        else:
            pov_filename = self.name
            errorcode, dir = self.assy.find_or_make_pov_files_directory()
            if errorcode:
                return None, None
    
        povrayini_file = os.path.normpath(os.path.join(dir, ini_filename))
        povrayscene_file = os.path.normpath(os.path.join(dir, pov_filename))
    
        #print "get_povfile_pair():\n  povrayini_file=", povrayini_file, "\n  povrayscene_file=", povrayscene_file
        return povrayini_file, povrayscene_file
    
    def render_scene(self, tmpscene=False):
        """Render scene. 
        If tmpscene is False, the INI and pov files are written to the 'POV-Ray Scene Files' directory.
        If tmpscene is True, the INI and pov files are written to a temporary directory (~/Nanorex/POV-Ray).
        Callers should set <tmpscene> = True when they want to render the scene but don't need to 
        save the files and create a POV-Ray Scene node (i.e. 'View > Raytrace Scene').
        The caller is responsible for adding the POV-Ray Scene node to the model tree.
        Returns errorcode and errortext.
        """
        ini, pov = self.get_povfile_pair(tmpscene)
        
        if ini:
            if not self.povrayscene_file:
                self.povrayscene_file = pov
                writepovfile(self.assy.part, self.assy.o, self.povrayscene_file)
            write_povray_ini_file(ini, self.povrayscene_file, self.width, self.height, self.output_type)
        else:
            return 1, "Problem getting POV-Ray INI filename."
        
        # Launch POV-Ray or MegaPOV
        errorcode, errortext = launch_povray_or_megapov(self.assy.w, ini) # Launch MegaPOV
            
        return errorcode, errortext # errorcode = 0 if successful.
      
    # Context menu item methods #######################################
    
    def __CM_Render_Scene(self):
        '''Method for "Render Scene" context menu.'''
        errorcode, errortext = self.render_scene()
        if errorcode:
            env.history.message( "Render Scene: " + redmsg(errortext) )

    pass # end of class PovrayScene
