# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
ops_files.py provides fileSlotsMixin for MWsemantics,
with file slot methods and related helper methods.

$Id$

Note: most other ops_*.py files provide mixin classes for Part,
not for MWsemantics like this one.

History:

bruce 050907 split this out of MWsemantics.py.
[But it still needs major cleanup and generalization.]
'''

from qt import QFileDialog, QMessageBox, QString
from assembly import assembly
import os
import platform

from constants import * # needed for at least globalParms
from fileIO import * # this might be needed for some of the many other modules it imports; who knows? [bruce 050418 comment]
    # (and it's certainly needed for the functions it defines, e.g. writepovfile.)
from files_pdb import readpdb, insertpdb, writepdb
from files_gms import readgms, insertgms
from files_mmp import readmmp, insertmmp, fix_assy_and_glpane_views_after_readmmp
from debug import print_compact_traceback

from HistoryWidget import greenmsg, redmsg

import preferences
import env

    
def fileparse(name): #bruce 050413 comment: see also filesplit and its comments.
    """breaks name into directory, main name, and extension in a tuple.
    fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')
    """
    m=re.match("(.*\/)*([^\.]+)(\..*)?",name)
    return ((m.group(1) or "./"), m.group(2), (m.group(3) or ""))


class fileSlotsMixin: #bruce 050907 moved these methods out of class MWsemantics
    "Mixin class to provide file-related methods for class MWsemantics. Has slot methods and their helper methods."
    
    def fileNew(self):
        """If this window is empty (has no assembly), do nothing.
        Else create a new empty one.
        """
        #bruce 050418 comment: this has never worked correctly to my knowledge,
        # and therefore it was made unavailable from the UI some time ago.
        from MWsemantics import MWsemantics #bruce 050907 (might have a recursive import problem if done at toplevel)
        foo = MWsemantics()
        foo.show()

    def fileInsert(self):
        
        self.history.message(greenmsg("Insert File:"))
         
        wd = globalParms['WorkingDirectory']
        fn = QFileDialog.getOpenFileName(wd,
                "Molecular machine parts (*.mmp);;Protein Data Bank (*.pdb);;GAMESS (*.out);;All of the above (*.pdb *.mmp *.out)",
                self )
                
        if not fn:
             self.history.message("Cancelled")
             return
        
        if fn:
            fn = str(fn)
            if not os.path.exists(fn):
                #bruce 050415: I think this should never happen;
                # in case it does, I added a history message (to existing if/return code).
                self.history.message( redmsg( "File not found: " + fn) )
                return

            if fn[-3:] == "mmp":
                try:
                    insertmmp(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting MMP file [%s]: " % fn )
                    self.history.message( redmsg( "Internal error while inserting MMP file: " + fn) )
                else:
                    self.assy.changed() # The file and the part are not the same.
                    self.history.message( "MMP file inserted: " + fn )
            
            if fn[-3:] in ["pdb","PDB"]:
                try:
                    insertpdb(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting PDB file [%s]: " % fn )
                    self.history.message( redmsg( "Internal error while inserting PDB file: " + fn) )
                else:
                    self.assy.changed() # The file and the part are not the same.
                    self.history.message( "PDB file inserted: " + fn )
            
            if fn[-3:] in ["out","OUT"]:
                try:
                    r = insertgms(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting GAMESS OUT file [%s]: " % fn )
                    self.history.message( redmsg( "Internal error while inserting GAMESS OUT file: " + fn) )
                else:
                    if r:
                        self.history.message( redmsg("File not inserted."))
                    else:
                        self.assy.changed() # The file and the part are not the same.
                        self.history.message( "GAMESS file inserted: " + fn )
                    
                    
            self.glpane.scale = self.assy.bbox.scale()
            self.glpane.gl_update()
            self.mt.mt_update()


    def fileOpen(self):
        
        self.history.message(greenmsg("Open File:"))
        
        if self.assy.has_changed():
            ret = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before opening a new part?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret==0: # Save clicked or Alt+S pressed or Enter pressed.
                ##Huaicai 1/6/05: If user canceled save operation, return 
                ## without letting user open another file
                if not self.fileSave(): return
                
            ## Huaicai 12/06/04. Don't clear it, user may cancel the file open action    
            elif ret==1: pass#self.__clear() 
            
            elif ret==2: 
                self.history.message("Cancelled.")
                return # Cancel clicked or Alt+C pressed or Escape pressed

        # Determine what directory to open.
        if self.assy.filename: odir, fil, ext = fileparse(self.assy.filename)
        else: odir = globalParms['WorkingDirectory']

        fn = QFileDialog.getOpenFileName(odir,
                "All Files (*.mmp *.pdb);;Molecular machine parts (*.mmp);;Protein Data Bank (*.pdb)",
                self )
                
        if not fn:
            self.history.message("Cancelled.")
            return

        if fn:
            self.__clear()
                
            fn = str(fn)
            if not os.path.exists(fn): return

            isMMPFile = False
            if fn[-3:] == "mmp":
                readmmp(self.assy,fn)
                    #bruce 050418 comment: we need to check for an error return
                    # and in that case don't clear or have other side effects on assy;
                    # this is not yet perfectly possible in readmmmp.
                self.history.message("MMP file opened: [" + fn + "]")
                isMMPFile = True
                
            if fn[-3:] in ["pdb","PDB"]:
                readpdb(self.assy,fn)
                self.history.message("PDB file opened: [" + fn + "]")

            dir, fil, ext = fileparse(fn)
            self.assy.name = fil
            self.assy.filename = fn
            self.assy.reset_changed() # The file and the part are now the same

#            self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
            self.update_mainwindow_caption()

            if isMMPFile:
                #bruce 050418 moved this code into a new function in files_mmp.py
                # (but my guess is it should mostly be done by readmmp itself)
                fix_assy_and_glpane_views_after_readmmp( self.assy, self.glpane)
            else: ###PDB or other file format        
                self.setViewFitToWindow()

            self.glpane.gl_update() #bruce 050418
            self.mt.mt_update()

    def fileSave(self):
        
        self.history.message(greenmsg("Save File:"))
        
        #Huaicai 1/6/05: by returning a boolean value to say if it is really 
        # saved or not, user may choose "Cancel" in the "File Save" dialog          
        if self.assy:
            if self.assy.filename: 
                self.saveFile(self.assy.filename)
                return True
            else: 
                return self.fileSaveAs()


    def fileSaveAs(self):
        if self.assy:
            if self.assy.filename:
                dir, fil, ext = fileparse(self.assy.filename)
                sdir = self.assy.filename
            else: 
                dir, fil = "./", self.assy.name
                ext = ".mmp"
                sdir = globalParms['WorkingDirectory']
        else:
            self.history.message( "Save Ignored: Part is currently empty." )
            return False

        if ext == ".pdb": sfilter = QString("Protein Data Bank (*.pdb)")
        else: sfilter = QString("Molecular machine parts (*.mmp)")
        
        fn = QFileDialog.getSaveFileName(sdir,
                    "Molecular Machine Part (*.mmp);;"\
                    "Protein Data Bank (*.pdb);;"\
                    "POV-Ray (*.pov);;"\
                    "Model MDL (*.mdl);;"\
                    "JPEG (*.jpg);;"\
                    "Portable Network Graphics (*.png)",
                    self, "IDONTKNOWWHATTHISIS",
                    "Save As",
                    sfilter)
        
        if fn:
            fn = str(fn)
            dir, fil, ext2 = fileparse(fn)
            ext =str(sfilter[-5:-1]) # Get "ext" from the sfilter. It *can* be different from "ext2"!!! - Mark
            safile = dir + fil + ext # full path of "Save As" filename
            
            if self.assy.filename != safile: # If the current part name and "Save As" filename are not the same...
                if os.path.exists(safile): # ...and if the "Save As" file exists...

                    # ... confirm overwrite of the existing file.
                    ret = QMessageBox.warning( self, self.name(),
                        "The file \"" + fil + ext + "\" already exists.\n"\
                        "Do you want to overwrite the existing file or cancel?",
                        "&Overwrite", "&Cancel", None,
                        0,      # Enter == button 0
                        1 )     # Escape == button 1

                    if ret==1: # The user cancelled
                        self.history.message( "Cancelled.  Part not saved." )
                        return False # Cancel clicked or Alt+C pressed or Escape pressed
            
            self.saveFile(safile)
            return True
            
        else: return False ## User canceled.
            

    def saveFile(self, safile):
        
        dir, fil, ext = fileparse(safile)
#            print "saveFile: ext = [",ext,"]"

        if ext == ".pdb": # Write PDB file.
            try:
                writepdb(self.assy, safile)
            except:
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                self.history.message(redmsg( "Problem saving PDB file: " + safile ))
            else:
                self.assy.filename = safile
                self.assy.name = fil
                self.assy.reset_changed() # The file and the part are now the same.
#                self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
                self.update_mainwindow_caption()
                self.history.message( "PDB file saved: " + self.assy.filename )
                self.mt.mt_update()
            
        elif ext == ".pov": # Write POV-Ray file
            try:
                writepovfile(self.assy, safile)
            except:
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                self.history.message(redmsg( "Problem saving POV-Ray file: " + safile ))
            else:
                self.history.message( "POV-Ray file saved: " + safile )
            
        elif ext == ".mdl": # Write MDL file
            try:
                writemdlfile(self.assy, safile)
            except:
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                self.history.message(redmsg( "Problem saving MDL file: " + safile ))
            else:
                self.history.message( "MDL file saved: " + safile )
            
        elif ext == ".jpg": # Write JPEG file
            try:
                image = self.glpane.grabFrameBuffer()
                image.save(safile, "JPEG", 85)
            except:
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                self.history.message(redmsg( "Problem saving JPEG file: " + safile ))
            else:
                self.history.message( "JPEG file saved: " + safile )
            
        elif ext == ".png": # Write PNG file
            try:
                image = self.glpane.grabFrameBuffer()
                image.save(safile, "PNG")
            except:
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                self.history.message(redmsg( "Problem saving PNG file: " + safile ))
            else:
                self.history.message( "PNG file saved: " + safile )
                    
        elif ext == ".mmp" : # Write MMP file
            try:
                tmpname = os.path.join(dir, '~' + fil + '.m~')
                self.assy.writemmpfile(tmpname)
            except:
                #bruce 050419 revised printed error message
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file [%s]: " % safile )
                self.history.message(redmsg( "Problem saving file: " + safile ))
                
                # If you want to see what was wrong with the MMP file, you
                # can comment this out so you can see what's in
                # the temp MMP file.  Mark 050128.
                if os.path.exists(tmpname):
                    os.remove (tmpname) # Delete tmp MMP file
            else:
                if os.path.exists(safile):
                    os.remove (safile) # Delete original MMP file

                os.rename( tmpname, safile) # Move tmp file to saved filename. 
                
                self.assy.filename = safile
                self.assy.name = fil
                self.assy.reset_changed() # The file and the part are now the same.
#                self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
                self.update_mainwindow_caption()
                self.history.message( "MMP file saved: " + self.assy.filename )
                self.mt.mt_update()
            
        else: # This should never happen.
            self.history.message(redmsg( "MWSemantics.py: fileSaveAs() - File Not Saved. Unknown extension:" + ext))

    def closeEvent(self,ce):
        #bruce 090507 comment: this method needs to be split in two,
        # with only the outer part (moved back to MWsemantics, still called closeEvent)
        # knowing ce arg and using isEventAccepted value (renamed),
        # and with inner part returning shouldEventBeAccepted, but staying here with its file-related code.
        # But for the sake of viewcvs and testing, I should not do this in the same commit
        # that splits this file (ops_files.py) out of MWsemantics.
        """  via File > Exit or clicking X titlebar button """
        isEventAccepted = True
        if not self.assy.has_changed():
            ce.accept()
        else:
            rc = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before exiting?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2

            if rc == 0:
                isFileSaved = self.fileSave() # Save clicked or Alt+S pressed or Enter pressed.
                ##Huaicai 1/6/05: While in the "Save File" dialog, if user chooses ## "Cancel", the "Exit" action should be ignored. bug 300
                if isFileSaved:
                    ce.accept()
                else:
                    ce.ignore()
                    isEventAccepted = False
            elif rc == 1:
                ce.accept()
            else:
                ce.ignore()
                isEventAccepted = False
        
        #if isEventAccepted: self.periodicTable.close()
            

    def fileClose(self):
        
        self.history.message(greenmsg("Close File:"))
        
        isFileSaved = True
        if self.assy.has_changed():
            ret = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before closing this part?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret==0: isFileSaved = self.fileSave() # Save clicked or Alt+S pressed or Enter pressed.
            elif ret==1:
                self.history.message("Changes discarded.")
            elif ret==2: 
                self.history.message("Cancelled.")
                return # Cancel clicked or Alt+C pressed or Escape pressed
        
        if isFileSaved: 
                self.__clear()
                self.assy.reset_changed() #bruce 050429, part of fixing bug 413
                self.win_update()


    def fileSetWorkDir(self):
        """Sets working directory"""

        self.history.message(greenmsg("Set Working Directory:"))
        
        wd = globalParms['WorkingDirectory']
        wdstr = "Current Working Directory - [" + wd  + "]"
        wd = QFileDialog.getExistingDirectory( wd, self, "get existing directory", wdstr, 1 )
        
        if not wd:
            self.history.message("Cancelled.")
            return
            
        if wd:
            wd = str(wd)
            wd = os.path.normpath(wd)
            globalParms['WorkingDirectory'] = wd
            
            self.history.message( "Working Directory set to " + wd )

            # bruce 050119: store this in prefs database so no need for ~/.ne1rc
            from preferences import prefs_context
            prefs = prefs_context()
            prefs['WorkingDirectory'] = wd
                
    def __clear(self):
        #bruce 050907 comment: this is only called from this mixin, so I moved it here from MWsemantics
        # even though its name-mangled name was thereby changed. It should really be given a normal name.
        # Some comments in other files still call it MWsemantics.__clear.
        
        # assyList refs deleted by josh 10/4
        self.assy = assembly(self, "Untitled")
#        self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.name + "]"))
        self.update_mainwindow_caption()
        self.glpane.setAssy(self.assy)
        self.assy.mt = self.mt
        
        ### Hack by Huaicai 2/1 to fix bug 369
        self.mt.resetAssy_and_clear() 

    pass # end of class fileSlotsMixin

# end
