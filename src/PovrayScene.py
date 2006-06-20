# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
PovrayScene.py - The POV-Ray Scene class.

$Id$

History:

mark 060601 - Created.

'''

__author__ = "Mark"

from Utility import SimpleCopyMixin, Node, imagename_to_pixmap
from povray import get_raytrace_scene_filenames, write_povray_ini_file, raytrace_scene_using_povray
from fileIO import writepovfile
from qt import Qt, QApplication, QCursor
from HistoryWidget import greenmsg, redmsg
import env, os, sys

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
            name = genPVSNum("%s-" % self.sym)
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
        "Opens POV-Ray Scene dialog with current parameters."
        self.assy.w.povrayscenecntl.setup(self)
        
    def writemmp(self, mapping):
        mapping.write("povrayscene (" + mapping.encode_name(self.name) + ") %d %d %s\n" % \
            (self.width, self.height, self.output_type))
        mapping.write("info povrayscene povrayscene_file = %s\n" % self.povrayscene_file)
            #&&& povrayscene_file is an abolute path. Needs to be a relative path. Mark 060613.
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
                self.povrayscene_file = val
                    #&&& This is an absolute path. Needs to be written a relative path in writemmp(). Mark 060613.
                    # Some fixup might also be needed in other methods which use this, like the following (split out by bruce 060620).
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
    
    def write_pvs_file(self):
        '''Writes a POV-Ray Scene file of the current scene in the GLPane.
        '''
        povray_ini, povray_scene = get_raytrace_scene_filenames(self.assy, self.name)
        
        if not povray_ini:
            # There was a problem. povray_scene contains a description the problem.
            env.history.message( cmd + redmsg(povray_scene) )
            return
        
        writepovfile(self.assy.part, self.assy.o, povray_scene)
        
        self.povrayscene_file = povray_scene
        
    def render_image(self, use_existing_pvs=False, create_image_node=False):
        '''Renders image from a new or existing POV-Ray Scene file.
        If <use_existing_pvs> is True, use the existing POV-Ray Scene file (if it exists).
        Creates an Image node in the model tree if <create_image_node> is True. NIY - Mark 060602.
        '''
        
        cmd = greenmsg("Render POV-Ray Scene: ")
        
        povray_ini, povray_scene = get_raytrace_scene_filenames(self.assy, self.name)
        
        if not povray_ini:
            # There was a problem. povray_scene contains a description the problem.
            env.history.message( cmd + redmsg(povray_scene) )
            return
        
        if use_existing_pvs and not os.path.exists(povray_scene):
            env.history.message( cmd + redmsg("POV-Ray Scene file does not exist.") )
            self.const_icon = imagename_to_pixmap("povrayscene-notfound.png")
                #&&& Need to update the model tree. Should the caller do this? I think so. Need to decide the best way.
                # There probably needs to be a more general and persistent way to periodically update file
                # nodes icons when their associated file goes AWOL and "not found" icons should be displayed.
                # Talk to Bruce about this. Mark 060613.
                # bruce 060620 replies: the above change of icon should probably be done in self.update_icon, not here,
                # but that needs cleanup re using wrong filename in history message;
                # and then that method should call mt_update if it changes the icon. ###@@@
            return
        
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        
        try:
            if not use_existing_pvs or not os.path.exists(povray_scene):
                # If <use_existing_pvs> is False or if the pvs file does not exist, write the pvs (.pov) file.
                writepovfile(self.assy.part, self.assy.o, povray_scene)
                #env.history.message( "POV-Ray Scene written to " + povray_scene )
            write_povray_ini_file(povray_ini, povray_scene, self.width, self.height, self.output_type)
            r, why = raytrace_scene_using_povray(self.assy, povray_ini)
            if r:
                env.history.message( cmd + redmsg(why) )
                return
        
        except Exception, e:
                env.history.message(cmd + redmsg(" - ".join(map(str, e.args))))
                
        QApplication.restoreOverrideCursor() # Restore the cursor
        
        return
    
    # Context menu item methods #######################################
    
    def __CM_Render_Image(self):
        '''Method for "Render Image" context menu.'''
        self.render_image(use_existing_pvs=True)

    pass # end of class PovrayScene
