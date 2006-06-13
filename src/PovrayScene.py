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

    #copyable_attrs = Node.copyable_attrs + ... # Need to talk with Bruce about this. Mark 060602.

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
        self.assy.w.povrayscenecntl.show(self)
        
    def writemmp(self, mapping):
        mapping.write("povrayscene (" + mapping.encode_name(self.name) + ") %d %d %s\n" % \
            (self.width, self.height, self.output_type))
        mapping.write("info leaf povrayscene_file = %s\n" % self.get_pvs_filename())
        self.writemmp_info_leaf(mapping)
        return

    def __str__(self):
        return "<povrayscene " + self.name + ">"
        
    def render_image(self, use_existing_pvs=False, create_image_node=False):
        '''Renders image from a new or existing POV-Ray Scene file.
        If <use_existing_pvs> is True, use the existing POV-Ray Scene file (if it exists).
        Creates an Image node in the model tree if <create_image_node> is True. NIY - Mark 060602.
        '''
        
        cmd = greenmsg("Render POV-Ray Scene: ")
        
        povray_ini, povray_scene = get_raytrace_scene_filenames(self.assy, self.name)
        
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
        
    def get_pvs_filename(self):
        '''Returns the absolute pathname of the POV-Ray Scene file based on the pvs name and the cwd of the assy.'''
        povray_ini, povray_scene = get_raytrace_scene_filenames(self.assy, self.name)
        return povray_scene
    
    # Context menu item methods #######################################
    
    def __CM_Render_Image(self):
        '''Method for "Render Image" context menu.'''
        self.render_image(use_existing_pvs=True)

    # "Display Image" removed. POV-Ray Scene files can be used to render an image; they are not images 
    # themselves, nor do they have any association with the image files they create. 
    # Creating an image from a POV-Ray Scene file will create an "Image" node. 
    # An Image node will likely have a "Display..." context menu allowing the user to open the image in a separate window.
    # - Mark 060612.
    #def __CM_Display_Image(self):
    #   '''Method for "Display Image" context menu. Try to display the
    #    image by any means available.'''
    #    # What if it's not a PNG? It could be a BMP.
    #    fn = '\'' + self.get_pvs_filename().replace('.pov', '.png') + '\''
    #    if os.system('display ' + fn) == 0:
    #        return
    #    if os.system('xv ' + fn) == 0:
    #        return
    #    cmd = greenmsg("Display POV-Ray Scene: ")
    #    env.history.message(cmd + redmsg('No image display program available'))

    pass # end of class PovrayScene
