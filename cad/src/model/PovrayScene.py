# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
PovrayScene.py - The POV-Ray Scene class.

@author: Mark
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

mark 060601 - Created.
"""

import os
from PyQt4.Qt import QDialog
from PyQt4.Qt import QPixmap
from PyQt4.Qt import QLabel
from PyQt4.Qt import QRect
from PyQt4.Qt import QSize
from PyQt4.Qt import QApplication

import foundation.env as env
from foundation.Utility import SimpleCopyMixin, Node
from utilities.icon_utilities import imagename_to_pixmap
from graphics.rendering.povray.povray import decode_povray_prefs, write_povray_ini_file, launch_povray_or_megapov
from graphics.rendering.povray.writepovfile import writepovfile
from utilities.Log import redmsg, orangemsg, greenmsg, _graymsg
from utilities import debug_flags
from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
from utilities.debug import print_compact_traceback

import re
from files.mmp.files_mmp_registration import MMP_RecordParser
from files.mmp.files_mmp_registration import register_MMP_RecordParser

POVNum = 0

def generate_povrayscene_name(assy, prefix, ext):
    """
    Returns a name for the POV-Ray Scene object.
    Make sure the filename that is derived from the new name does not already exist.
    """
    global POVNum
    name = ''
    name_exists = True
    while name_exists:
        POVNum += 1
        name = prefix + "-" + str(POVNum) + ext  # (i.e. "POV-Ray Scene-1.pov")
            # TODO: use gensym, then no need for POVNum
        if not os.path.exists(get_povrayscene_filename_derived_from_name(assy, name)):
            name_exists = False
            return name

def get_povrayscene_filename_derived_from_name(assy, name):
    """
    Returns the full (absolute) path of the POV-Ray Scene filename for <assy> derived from <name>.
    """
    errorcode, dir = assy.find_or_make_pov_files_directory()
    if errorcode:
        return "filename_does_not_exist"
    povrayscene_file = os.path.normpath(os.path.join(dir, name))
    #print "get_povrayscene_filename_derived_from_name(): povrayscene_file=", povrayscene_file
    return povrayscene_file

# ==

class PovrayScene(SimpleCopyMixin, Node):
    """
    A POV-Ray Scene is a .pov file that can be used to render images, accessible from the Model Tree as a node.
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

        self.const_pixmap = imagename_to_pixmap("modeltree/povrayscene.png")
            # note: this might be changed later; this value is not always correct; that may be a bug when this node is copied.
            # [bruce 060620 comment]

        Node.__init__(self, assy, name)
        if params:
            self.set_parameters(params)
        else:
            def_params = (assy.o.width, assy.o.height, 'png')
            self.set_parameters(def_params)

        return

    def set_parameters(self, params): #bruce 060620 removed name from params list
        """
        Sets all parameters in the list <params> for this POV-Ray Scene.
        """
        self.width, self.height, self.output_type = params
        self.povrayscene_file = get_povrayscene_filename_derived_from_name(self.assy, self.name) # Mark 060702.
        self.assy.changed()

    def get_parameters(self): #bruce 060620 removed name from params list
        """
        Returns list of parameters for this POV-Ray Scene.
        """
        return (self.width, self.height, self.output_type)

    def edit(self):
        """
        Opens POV-Ray Scene properties dialog with current parameters.
        """
        self.assy.w.povrayscenecntl.setup(self)

    def writemmp(self, mapping):
        mapping.write("povrayscene (" + mapping.encode_name(self.name) + ") %d %d %s\n" % \
            (self.width, self.height, self.output_type))

        # Write relative path of POV-Ray Scene file into info record.
        # For Alpha 8, the name and the basename are usually the same.
        # The only way I'm aware of that the name and the basename would be
        # different is if the user renamed the node in the Model Tree.
        # [Or they might move the file in the OS, and edit the node's mmp record,
        #  in ways which ought to be legal according to the documentation. bruce 060707 comment]

        mapping.write("info povrayscene povrayscene_file = POV-Ray Scene Files/%s\n" % self.name) # Relative path.

        # Note: Users will assume when they rename an existing MMP file, all the POV-Ray Scene files will still be associated
        # with the MMP file. This is handled by separate code in Save As which copies those files, or warns when it can't.

        self.writemmp_info_leaf(mapping)
        return

    def readmmp_info_povrayscene_setitem( self, key, val, interp ):
        """
        This is called when reading an mmp file, for each "info povrayscene" record
        which occurs right after this node is read and no other (povrayscene) node has been read.

        Key is a list of words, val a string; the entire record format
        is presently [060108] "info povrayscene <key> = <val>", and there is exactly
        one word in <key>, "povrayscene_file". <val> is the povrayscene filename.
        <interp> is not currently used.
        """
        if len(key) != 1:
            if debug_flags.atom_debug:
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
        """
        Update our icon according to whether our file exists or not (or use the boolean passed as found, if one is passed).
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
            self.const_pixmap = imagename_to_pixmap("modeltree/povrayscene.png")
        else:
            self.const_pixmap = imagename_to_pixmap("modeltree/povrayscene-notfound.png")
            if print_missing_file:
                msg = redmsg("POV-Ray Scene file [" + filename + "] does not exist.") #e some callers would prefer orangemsg, cmd, etc.
                env.history.message(msg)
        return not found

    def __str__(self):
        return "<povrayscene " + self.name + ">"

    def write_povrayscene_file(self):
        """
        Writes a POV-Ray Scene file of the current scene in the GLPane to the POV-Ray Scene Files directory.
        If successful, returns errorcode=0 and the absolute path of povrayscene file.
        Otherwise, returns errorcode=1 with text describing the problem writing the file.
        """
        ini, pov, out = self.get_povfile_trio() # pov includes the POV-Ray Scene Files directory in its path.
        if not ini:
            return 1, "Can't get POV-Ray Scene filename"
        #print "write_povrayscene_file(): povrayscene_file=", pov
        writepovfile(self.assy.part, self.assy.o, pov)
        return 0, pov

    def get_povfile_trio(self, tmpfile = False):
        """
        Makes up and returns the trio of POV-Ray filenames (as absolute paths):
        POV-Ray INI file, POV-Ray Scene file, and output image filename.
        If there was any problem, returns None, None, None.
        <tmpfile> flag controls how we choose their directory.
        [WARNING: current code may call it more than once during the same operation,
         so it needs to be sure to return the same names each time! [bruce guess 060711]]
        """
        # The ini, pov and out files must be in the same directory due to POV-Ray's I/O Restriction feature. Mark 060625.

        ini_filename = "povray.ini"
        # Critically important: POV-Ray uses the INI filename as an argument; it cannot have any whitespaces.
        # This is a POV-Ray bug on Windows only. For more information about this problem, see:
        # http://news.povray.org/povray.windows/thread/%3C3e28a17f%40news.povray.org%3E/?ttop=227783&toff=150
        # Mark 060624.

        if tmpfile:
            pov_filename = "raytracescene.pov"
            dir = find_or_make_Nanorex_subdir("POV-Ray")
            if not dir:
                return None, None, None
        else:
            pov_filename = self.name
            errorcode, dir = self.assy.find_or_make_pov_files_directory()
            if errorcode:
                return None, None, None ###e ought to return something containing dir (errortext) instead

        # Build image output filename <out_filename>.
        # WARNING and BUG: this code is roughly duplicated in povray.py, and they need to match;
        # and .bmp is probably not properly supported for Mac in povray.py. [bruce 060711 comment]
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

    def raytrace_scene(self, tmpscene = False):
        """
        Render scene.
        If tmpscene is False, the INI and pov files are written to the 'POV-Ray Scene Files' directory.
        If tmpscene is True, the INI and pov files are written to a temporary directory (~/Nanorex/POV-Ray).
        Callers should set <tmpscene> = True when they want to render the scene but don't need to
        save the files and create a POV-Ray Scene node in the MT (i.e. 'View > POV-Ray').
        The caller is responsible for adding the POV-Ray Scene node (self) to the model tree, if desired.
        Prints any necessary error messages to history; returns nothing.
        """
        #bruce 060710 corrected inaccuracies in docstring
        cmd = greenmsg("POV-Ray: ")
        if env.debug():
            #bruce 060707 (after Windows A8, before Linux/Mac A8)
            # compromise with what's best, so it can be ok for A8 even if only on some platforms
            env.history.message(_graymsg("POV-Ray: "))
            env.history.h_update()
            env.history.widget.update() ###@@@ will this help? is it safe? should h_update do it?

        ini, pov, out = self.get_povfile_trio(tmpscene)

        if not ini:
            ## return 1, "Problem getting POV-Ray filename trio."
            # [bruce 060710 replaced the above with the following, since it no longer matches the other return statements, or any calls]
            env.history.message(cmd + redmsg("Problem getting POV-Ray filename trio."))
                ###e should fix this to improve the message, by including errortext from get_povfile_trio retval (which is nim)
            return

        if tmpscene or not os.path.isfile(self.povrayscene_file):
            # write a new .pov file and save its name in self
            #
            #bruce 060711 comment (about a bug, not yet reported): ###@@@
            #   If an existing pov file has unexpectedly gone missing,
            # this code (I think) rerenders the current model, without even informing the user of the apparent error.
            #   That is extremely bad behavior, IMHO. What it ought to do is put up a dialog to inform the
            # user that the file is missing, and allow one of three actions: cancel, rerender current model,
            # or browse for the file to try to find it. If that browse is cancelled, it should offer the other
            # options, or if that finds the file but it's external, it should offer to copy it or make an
            # external link (or cancel), and then to continue or do no more. All this is desirable for any kind
            # of file node, not just PovrayScene. As it is, this won't be fixed for Mac A8; don't know about 8.1.
            self.povrayscene_file = pov
            writepovfile(self.assy.part, self.assy.o, self.povrayscene_file)
                # bruce 060711 question (possible bug): what sets self.width, self.height,  self.output_type in this case,
                # if the ones used by writepovfile differ from last time they were set in this node?
                # Guess: nothing does (bug, not yet reported). ###@@@

        # figure out renderer to use (POV-Ray or MegaPOV), its path, and its include_dir
        # (note: this contains most of the error checks that used to be inside launch_povray_or_megapov)
        # [bruce 060711 for Mac A8]
        win = self.assy.w
        ask_for_help = True # give user the chance to fix problems in the prefs dialog
        errorcode, errortext_or_info = decode_povray_prefs(win, ask_for_help, greencmd = cmd)
        if errorcode:
            errortext = errortext_or_info
            env.history.message(cmd + redmsg(errortext)) # redmsg in Mac A8, orangemsg in Windows A8 [bruce 060711]
            return
        info = errortext_or_info
        (program_nickname, program_path, include_dir) = info

        pov = self.povrayscene_file ###k btw, is this already true?

        #k is out equal to whatever in self might store it, if anything? maybe it's not stored in self.

        write_povray_ini_file(ini, pov, out, info, self.width, self.height, self.output_type)

        if tmpscene:
            msg = "Rendering scene. Please wait..."
        else:
            msg = "Rendering raytrace image from POV-Ray Scene file. Please wait..."
        env.history.message(cmd + msg)
        env.history.h_update() #bruce 060707 (after Windows A8, before Linux/Mac A8): try to make this message visible sooner
            # (doesn't work well enough, at least on Mac -- do we need to emit it before write_povray_ini_file?)
        env.history.widget.update() ###@@@ will this help? is it safe? should h_update do it?
        ###e these history widget updates fail to get it to print. Guess: we'd need qapp process events. Fix after Mac A8.
        # besides, we need this just before the launch call, not here.

        if os.path.exists(out): #bruce 060711 in Mac A8 not Windows A8 (probably all of Mac A8 code will also be in Linux A8)
            #e should perhaps first try moving the file to a constant name, so user could recover it manually if they wanted to
            #e (better yet, we should also try to avoid this situation when choosing the filename)
            msg = "Warning: image file already exists; removing it first [%s]" % out
            env.history.message(cmd + orangemsg(msg))
            try:
                os.remove(out)
            except:
                # this code was tested with a fake exception [060712 1041am]
                msg1 = "Problem removing old image file"
                msg2a = " [%s]" % out
                msg2b = "-- will try to overwrite it, "\
                      "but undetected rendering errors might leave it unchanged [%s]" % out
                print_compact_traceback("%s: " % (msg1 + msg2a))
                msg = redmsg(msg1) + msg2b
                #e should report the exception text in the history, too
                env.history.message(msg)
            pass

        # Launch raytrace program (POV-Ray or MegaPOV)
        errorcode, errortext = launch_povray_or_megapov(win, info, ini)

        if errorcode:
            env.history.message(cmd + redmsg(errortext)) # redmsg in Mac A8, orangemsg in Windows A8 [bruce 060711]
            return

        #bruce 060707 (after Windows A8, before Linux/Mac A8): make sure the image file exists.
        # (On Mac, on that date [not anymore, 060710], we get this far (no error return, or maybe another bug hid one),
        # but the file is not there.)
        if not os.path.exists(out):
            msg = "Error: %s program finished, but failed to produce expected image file [%s]" % (program_nickname, out)
            env.history.message(cmd + redmsg(msg))
            return

        env.history.message(cmd + "Rendered image: " + out)

        # Display image in a window.
        imageviewer = ImageViewer(out, win)
            #bruce 060707 comment: if the file named <out> doesn't exist, on Mac,
            # this produces a visible and draggable tiny window, about 3 pixels wide and maybe 30 pixels high.
        imageviewer.display()

        return # from raytrace_scene out

    def kill(self, require_confirmation = True):
        """
        Delete the POV-Ray Scene node and its associated .pov file if it exists.
        If <require_confirmation> is True, make the user confirm first [for deleting the file and the node both, as one op].
        [WARNING: user confirmation is not yet implemented.]
        Otherwise, delete the file without user confirmation.
        """
        if os.path.isfile(self.povrayscene_file):
            if 0: # Don't require confirmation for A8. Mark 060701. [but see comment below about why this is a bad bug]
            # if require_confirmation:
                msg = "Please confirm that you want to delete " + self.name
                from widgets.widget_helpers import PleaseConfirmMsgBox
                confirmed = PleaseConfirmMsgBox( msg)
                if not confirmed:
                    return
            # warn the user that you are about to remove what might be an irreplaceable rendering of a prior version
            # of the main file, without asking, or even checking if other nodes in this assy still point to it
            # [this warning added by bruce 060711 for Mac A8, not present in Windows A8]
            env.history.message(orangemsg("Warning: deleting file [%s]" % self.povrayscene_file))
            # do it
            os.remove(self.povrayscene_file)
            #bruce 060711 comment -- the above policy is a dangerous bug, since you can copy a node (not changing the filename)
            # and then delete one of the copies. This should not silently delete the file!
            # (Besides, even if you decide not to delete the file, .kill() should still delete the node.)
            #   This behavior is so dangerous that I'm tempted to fix it for Mac A8 even though it's too late
            # to fix it for Windows A8. Certainly it ought to be reported and releasenoted. But I think I will refrain
            # from the temptation to fix it for Mac A8, since doing it well is not entirely trivial, and any big bug-difference
            # in A8 on different platforms might cause confusion. But at least I will add a history message, so the user knows
            # right away if it caused a problem. And it needs to be fixed decently well for A8.1. ###@@@
            #   As for a better behavior, it would be good (and not too hard) to find out if other nodes
            # in the same assy point to the same file, and not even ask (just don't delete the file) if they do.
            # If not, ask, but always delete the node itself.
            #   But this is not trivial, since during a recursive kill of a Group, I'm not sure we can legally scan the tree.
            # (And if we did, it would then be quadratic time to delete a very large series of POV-Ray nodes.)
            # So we need a dictionary from filenames to lists or dicts of nodes that might refer to that filename.
            #   Of course there should also (for any filenode) be CM commands to delete or rename the file,
            # or (if other nodes also point to it) to copy it so this node owns a unique one.
        Node.kill(self)

    # == Context menu item methods

    def __CM_Raytrace_Scene(self):
        """
        Method for "Raytrace Scene" context menu.
        """
        self.raytrace_scene()

    pass # end of class PovrayScene

# ==

# ImageViewer class for displaying the image after it is rendered. Mark 060701.
class ImageViewer(QDialog):
    """
    ImageViewer displays the POV-Ray image <image_filename> after it has been rendered.
    """
    def __init__(self,image_filename,parent = None,name = None,modal = 0,fl = 0):
        #QDialog.__init__(self,parent,name,modal,fl)
        QDialog.__init__(self,parent)

        self.image = QPixmap(image_filename)
        width = self.image.width()
        height = self.image.height()
        caption = image_filename + " (" + str(width) + " x " + str(height) + ")"
        self.setWindowTitle(caption)

        if name is None:
            name = "ImageViewer"
        self.setObjectName(name)

        self.pixmapLabel = QLabel(self)
        self.pixmapLabel.setGeometry(QRect(0, 0, width, height))
        self.pixmapLabel.setPixmap(self.image)
        self.pixmapLabel.setScaledContents(1)

        self.resize(QSize(width, height).expandedTo(self.minimumSizeHint()))

    def display(self):
        """
        Display the image in the ImageViewer, making sure it isn't larger than the desktop size.
        """
        if QApplication.desktop().width() > self.image.width() + 10 and \
           QApplication.desktop().height() > self.image.height() + 30:
            self.show()
        else:
            self.showMaximized()
            # No scrollbars provided with showMaximized. The image is clipped if it is larger than the screen.
            # Probably need to use a QScrollView for large images. Mark 060701.
        return
    pass

# ==

# POV-Ray Scene record format:
pvs_pat = re.compile("povrayscene \((.+)\) (\d+) (\d+) (.+)")

class _MMP_RecordParser_for_PovrayScene( MMP_RecordParser): #bruce 071024
    """
    Read the MMP record for a POV-Ray Scene as:

    povrayscene (name) width height output_type
    """
    def read_record(self, card):
        m = pvs_pat.match(card)
        name = m.group(1)
        name = self.decode_name(name)
        width = int(m.group(2))
        height = int(m.group(3))
        output_type = m.group(4)
        params = width, height, output_type
        pvs = PovrayScene(self.assy, name, params)
        self.addmember(pvs)
        # for interpreting "info povrayscene" records:
        self.set_info_object('povrayscene', pvs)
        return
    pass

def register_MMP_RecordParser_for_PovrayScene():
    """
    [call this during init, before reading any mmp files]
    """
    register_MMP_RecordParser( 'povrayscene', _MMP_RecordParser_for_PovrayScene )
    return

# end

