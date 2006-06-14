# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
PovrayScene.py - The POV-Ray Scene class.

$Id$

History:

mark 060601 - Created.

'''

__author__ = "Mark"

from Utility import SimpleCopyMixin, Node, imagename_to_pixmap, genViewNum
from povray import get_raytrace_scene_filenames, write_povray_ini_file, raytrace_scene_using_povray
from fileIO import writepovfile
from qt import Qt, QApplication, QCursor
from HistoryWidget import greenmsg, redmsg
import env, os, sys

class PovrayScene(SimpleCopyMixin, Node):
    """A POV-Ray Scene is a .pov file that can be used to render images, accessible from the Model Tree as a node.
    """

    sym = "POV-Ray Scene"
    povrayscene_file = '' #&&& This is the absolute path to the povray scene file. This needs to be the relative path.

    copyable_attrs = Node.copyable_attrs + ('width', 'height', 'output_type', 'povrayscene_file')
        #&&& This doesn't work. Does it have something to do with <povrayscene_file> missing from set_parameters?
        #&&& Ask Bruce. Mark 060613.

    def __init__(self, assy, params):
        self.assy = assy
        self.set_parameters(params)
        self.const_icon = imagename_to_pixmap("povrayscene.png")
        if not self.name: 
            # Name is only generated here when called by "View > Raytrace Scene": ops_view.viewRaytraceScene().
            self.name = genViewNum("%s-" % self.sym)
        Node.__init__(self, assy, self.name)
        return
        
    def set_parameters(self, params):
        '''Sets all parameters in the list <params> for this POV-Ray Scene.
        '''
        self.name, self.width, self.height, self.output_type = params
        self.assy.changed()
        
    def get_parameters(self):
        '''Returns list of parameters for this POV-Ray Scene.
        '''
        return (self.name, self.width, self.height, self.output_type)

    def readmmp_info_leaf_setitem( self, key, val, interp ): #bruce 060522
        "[extends superclass method]"
        if key[0] == 'povrayscene' and len(key) == 2:
            # key[1] is the encoding, and val is one line in the comment
            self._add_line(val, key[1])
        else:
            Node.readmmp_info_leaf_setitem( self, key, val, interp)
        return
    
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
        is presently [060108] "info espimage <key> = <val>", and there is exactly
        one word in <key>, "povrayscene_file". <val> is the povrayscene filename.
        <interp> is not currently used.
        """
        if len(key) != 1:
            if platform.atom_debug:
                print "atom_debug: fyi: info espimage with unrecognized key %r (not an error)" % (key,)
            return
        if key[0] == 'povrayscene_file':
            if val:
                self.povrayscene_file = val
                    #&&& This is an absolute path. Needs to be written a relative path in writemmp(). Mark 060613.
                if os.path.exists(self.povrayscene_file):
                    self.const_icon = imagename_to_pixmap("povrayscene.png")
                else:
                    self.const_icon = imagename_to_pixmap("povrayscene-notfound.png")
                    msg = redmsg("info povrayscene povrayscene_file = " + val + ". File does not exist.")
                    env.history.message(msg)
            pass
        return

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
                # There probably needs to be a more general and persistant way to periodically update file
                # nodes icons when their associated file goes AWOL and "not found" icons should be displayed.
                # Talk to Bruce about this. Mark 060613.
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
