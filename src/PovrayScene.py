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
from qt import *
from HistoryWidget import redmsg, orangemsg, greenmsg
import env, os, sys
from platform import find_or_make_any_directory, find_or_make_Nanorex_subdir

POVNum = 0

def generate_povrayscene_name(assy, prefix, ext):
    """Returns a name for the POV-Ray Scene object.
    Make sure the filename that is derived from the new name does not already exist.
    """
    global POVNum
    name = ''
    name_exists = True
    while name_exists:
        POVNum += 1
        name = prefix + "-" + str(POVNum) + ext  # (i.e. "POV-Ray Scene-1.pov")
        if not os.path.exists(get_povrayscene_filename_derived_from_name(assy, name)):
            name_exists = False
            return name

def get_povrayscene_filename_derived_from_name(assy, name):
    """Returns the full (absolute) path of the POV-Ray Scene filename for <assy> derived from <name>.
    """
    errorcode, dir = assy.find_or_make_pov_files_directory()
    if errorcode:
        return "filename_does_not_exist" 
    povrayscene_file = os.path.normpath(os.path.join(dir, name))
    #print "get_povrayscene_filename_derived_from_name(): povrayscene_file=", povrayscene_file
    return povrayscene_file

class PovrayScene(SimpleCopyMixin, Node):
    """A POV-Ray Scene is a .pov file that can be used to render images, accessible from the Model Tree as a node.
    """

    sym = "POV-Ray Scene"
    extension = ".pov"
    povrayscene_file = ''

    width = height = output_type = None #bruce 060620, might not be needed
    
    copyable_attrs = Node.copyable_attrs + ('width', 'height', 'output_type', 'povrayscene_file')

    def __init__(self, assy, name, params = None):
        #bruce 060620 removed name from params list, made that optional, made name a separate argument,
        # all to make this __init__ method compatible with that of other nodes (see above for one reason);
        # also revised this routine in other ways, e.g. to avoid redundant sets of self.assy and self.name
        # (which are set by Node.__init__).
        if not name: 
            # [Note: this code might be superceded by code in Node.__init__ once nodename suffix numbers are revised.]
            # If this code is superceded, Node.__init__ must provide a way to verify that the filename (derived from the name)
            # doesn't exist, since this would be an invalid name. Mark 060702.
            name = generate_povrayscene_name(assy, self.sym, self.extension)
        Node.__init__(self, assy, name)
        if params:
            self.set_parameters(params)
        else:
            def_params = (assy.o.width, assy.o.height, 'png')
            self.set_parameters(def_params)
        self.const_icon = imagename_to_pixmap("povrayscene.png")
            # note: this might be changed later; this value is not always correct; that may be a bug when this node is copied.
            # [bruce 060620 comment]
        return
            
    def set_parameters(self, params): #bruce 060620 removed name from params list
        '''Sets all parameters in the list <params> for this POV-Ray Scene.
        '''
        self.width, self.height, self.output_type = params
        self.povrayscene_file = get_povrayscene_filename_derived_from_name(self.assy, self.name) # Mark 060702.
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
        
        # Write relative path of POV-Ray Scene file into info record.
        # For Alpha 8, the name and the basename are usually the same.
        # The only way I'm aware of that the name and the basename would be 
        # different is if the user renamed the node in the Model Tree.
        mapping.write("info povrayscene povrayscene_file = POV-Ray Scene Files/%s\n" % self.name) # Relative path.
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
        ini, pov, out = self.get_povfile_trio() # pov includes the POV-Ray Scene Files directory in its path.
        if not ini:
            return 1, "Can't get POV-Ray Scene filename"
        #print "write_povrayscene_file(): povrayscene_file=", pov
        writepovfile(self.assy.part, self.assy.o, pov)
        return 0, pov
    
    def get_povfile_trio(self, tmpfile = False):
        """Returns the trio of POV-Ray filenames: POV-Ray INI, POV-Ray Scene and output image. 
        If there was any problem, returns None.
        """
    
        # The ini, pov and out files must exist in the same directory due to POV-Ray's I/O Restriction feature. Mark 060625.
    
        ini_filename = "povray.ini"
        # Critically important: POV-Ray uses the INI filename as an argument; it cannot have any whitespaces.
        # This is a POV-Ray bug on Windows only. For more information about this problem, see:
        # http://news.povray.org/povray.windows/thread/%3C3e28a17f%40news.povray.org%3E/?ttop=227783&toff=150
        # Mark 060624.
    
        if tmpfile:
            pov_filename = "raytracescene.pov"
            from platform import find_or_make_Nanorex_subdir
            dir = find_or_make_Nanorex_subdir("POV-Ray")
            if not dir:
                return None, None, None
        else:
            pov_filename = self.name
            errorcode, dir = self.assy.find_or_make_pov_files_directory()
            if errorcode:
                return None, None, None
        
        # Build image output filename <out_filename>.
        if self.output_type == 'bmp':
            output_ext = '.bmp'
        else: # default
            output_ext = '.png'
        base, ext = os.path.splitext(pov_filename)
        out_filename = base + output_ext
    
        ini = os.path.normpath(os.path.join(dir, ini_filename))
        pov = os.path.normpath(os.path.join(dir, pov_filename))
        out = os.path.normpath(os.path.join(dir, out_filename))
    
        #print "get_povfile_trio():\n  ini=", ini, "\n  pov=", pov, "\n  out=", out
        return ini, pov, out
    
    def raytrace_scene(self, tmpscene=False):
        """Render scene. 
        If tmpscene is False, the INI and pov files are written to the 'POV-Ray Scene Files' directory.
        If tmpscene is True, the INI and pov files are written to a temporary directory (~/Nanorex/POV-Ray).
        Callers should set <tmpscene> = True when they want to render the scene but don't need to 
        save the files and create a POV-Ray Scene node (i.e. 'View > Raytrace Scene').
        The caller is responsible for adding the POV-Ray Scene node to the model tree.
        Returns errorcode and errortext.
        """
        ini, pov, out = self.get_povfile_trio(tmpscene)
        
        if ini:
            if tmpscene or not os.path.isfile(self.povrayscene_file):
                self.povrayscene_file = pov
                writepovfile(self.assy.part, self.assy.o, self.povrayscene_file)
            write_povray_ini_file(ini, self.povrayscene_file, self.width, self.height, self.output_type)
        else:
            return 1, "Problem getting POV-Ray filename trio."
        
        cmd = greenmsg("Raytrace Scene: ")
        if tmpscene:
            msg = "Rendering scene. Please wait..."
        else:
            msg = "Rendering raytrace image from POV-Ray Scene file. Please wait..."
        env.history.message(cmd + msg)
        
        # Launch raytrace program (POV-Ray or MegaPOV)
        errorcode, errortext = launch_povray_or_megapov(self.assy.w, ini)
        
        if errorcode:
            env.history.message(cmd + orangemsg(errortext))
            return
        
        env.history.message(cmd + "Rendered image: " + out)
        
        # Display image in a window.
        imageviewer = ImageViewer(out, env.mainwindow())
        imageviewer.display()
    
    def kill(self, require_confirmation=True):
        """Delete the POV-Ray Scene node and its associated .pov file if it exists.
        If <require_confirmation> is True, make the user confirm first. Otherwise, delete the file without user confirmation.
        """
        if os.path.isfile(self.povrayscene_file):
            if 0: # Don't require confirmation for A8. Mark 060701.
            # if require_confirmation: 
                msg = "Please confirm that you want to delete " + self.name
                from widgets import PleaseConfirmMsgBox
                confirmed = PleaseConfirmMsgBox( msg)
                if not confirmed:
                    return
            # do it
            os.remove(self.povrayscene_file)
        Node.kill(self)
        
    # Context menu item methods #######################################
    
    def __CM_Raytrace_Scene(self):
        '''Method for "Raytrace Scene" context menu.'''
        self.raytrace_scene()

    pass # end of class PovrayScene

# ImageViewer class for displaying the image after it is rendered. Mark 060701.
class ImageViewer(QDialog):
    """ImageViewer displays the POV-Ray image <image_filename> after it has been rendered.
    """
    def __init__(self,image_filename,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image = QPixmap(image_filename)
        width = self.image.width()
        height = self.image.height()
        caption = image_filename + " (" + str(width) + " x " + str(height) + ")"
        self.setCaption(caption)

        if not name:
            self.setName("ImageViewer")

        self.pixmapLabel = QLabel(self,"pixmapLabel")
        self.pixmapLabel.setGeometry(QRect(0, 0, width, height))
        self.pixmapLabel.setPixmap(self.image)
        self.pixmapLabel.setScaledContents(1)

        self.resize(QSize(width, height).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)
    
    def display(self):
        """Display the image in the ImageViewer, making sure it isn't larger than the desktop size.
        """
        if QApplication.desktop().width() > self.image.width() + 10 and \
           QApplication.desktop().height() > self.image.height() + 30:
            self.show()
        else:
            self.showMaximized() 
            # No scrollbars provided with showMaximized. The image is clipped if it is larger than the screen.
            # Probably need to use a QScrollView for large images. Mark 060701.
