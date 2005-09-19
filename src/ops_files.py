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

bruce 050913 used env.history in some places.
'''

from qt import QFileDialog, QMessageBox, QString, qApp, QSettings
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
        
        env.history.message(greenmsg("Insert File:"))
         
        wd = globalParms['WorkingDirectory']
        fn = QFileDialog.getOpenFileName(wd,
                "Molecular machine parts (*.mmp);;Protein Data Bank (*.pdb);;GAMESS (*.out);;All of the above (*.pdb *.mmp *.out)",
                self )
                
        if not fn:
             env.history.message("Cancelled")
             return
        
        if fn:
            fn = str(fn)
            if not os.path.exists(fn):
                #bruce 050415: I think this should never happen;
                # in case it does, I added a history message (to existing if/return code).
                env.history.message( redmsg( "File not found: " + fn) )
                return

            if fn[-3:] == "mmp":
                try:
                    insertmmp(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting MMP file [%s]: " % fn )
                    env.history.message( redmsg( "Internal error while inserting MMP file: " + fn) )
                else:
                    self.assy.changed() # The file and the part are not the same.
                    env.history.message( "MMP file inserted: " + fn )
            
            if fn[-3:] in ["pdb","PDB"]:
                try:
                    insertpdb(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting PDB file [%s]: " % fn )
                    env.history.message( redmsg( "Internal error while inserting PDB file: " + fn) )
                else:
                    self.assy.changed() # The file and the part are not the same.
                    env.history.message( "PDB file inserted: " + fn )
            
            if fn[-3:] in ["out","OUT"]:
                try:
                    r = insertgms(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting GAMESS OUT file [%s]: " % fn )
                    env.history.message( redmsg( "Internal error while inserting GAMESS OUT file: " + fn) )
                else:
                    if r:
                        env.history.message( redmsg("File not inserted."))
                    else:
                        self.assy.changed() # The file and the part are not the same.
                        env.history.message( "GAMESS file inserted: " + fn )
                    
                    
            self.glpane.scale = self.assy.bbox.scale()
            self.glpane.gl_update()
            self.mt.mt_update()


    def fileOpen(self, recentedFile=None):
        '''By default, users open a file through 'Open File' dialog. If <recentFile> is provided, it means user
           is openning a file named <recentFile> through the 'Recent Files' menu list. The file may or may not exist. '''
        env.history.message(greenmsg("Open File:"))
        
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
                env.history.message("Cancelled.")
                return # Cancel clicked or Alt+C pressed or Escape pressed

        # Determine what directory to open.
        if self.assy.filename: odir, fil, ext = fileparse(self.assy.filename)
        else: odir = globalParms['WorkingDirectory']

        if recentedFile:
            if not os.path.exists(recentedFile):
              QMessageBox.warning( self, self.name(),
                "This file doesn't exist any more.", QMessageBox.Ok, QMessageBox.NoButton)
              return
            
            fn = recentedFile
        else:
            fn = QFileDialog.getOpenFileName(odir,
                    "All Files (*.mmp *.pdb);;Molecular machine parts (*.mmp);;Protein Data Bank (*.pdb)",
                    self )
                    
            if not fn:
                env.history.message("Cancelled.")
                return
        
        if fn:
            self._updateRecentFileList(fn)

            self.__clear() # leaves glpane.mode as nullmode, as of 050911
            self.glpane.start_using_mode( '$DEFAULT_MODE') #bruce 050911 [now needed here, to open files in default mode]
                
            fn = str(fn)
            if not os.path.exists(fn): return

            #k Can that return ever happen? Does it need an error message?
            # Should preceding clear and modechange be moved down here??
            # (Moving modechange even farther below would be needed,
            #  if we ever let the default mode be one that cares about the
            #  model or viewpoint when it's entered.)
            # [bruce 050911 questions]

            isMMPFile = False
            if fn[-3:] == "mmp":
                readmmp(self.assy,fn)
                    #bruce 050418 comment: we need to check for an error return
                    # and in that case don't clear or have other side effects on assy;
                    # this is not yet perfectly possible in readmmmp.
                env.history.message("MMP file opened: [" + fn + "]")
                isMMPFile = True
                
            if fn[-3:] in ["pdb","PDB"]:
                readpdb(self.assy,fn)
                env.history.message("PDB file opened: [" + fn + "]")

            dir, fil, ext = fileparse(fn)
            ###@@@e could replace some of following code with new method just now split out of saved_main_file [bruce 050907 comment]
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
        
        env.history.message(greenmsg("Save File:"))
        
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
            env.history.message( "Save Ignored: Part is currently empty." )
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
                        env.history.message( "Cancelled.  Part not saved." )
                        return False # Cancel clicked or Alt+C pressed or Escape pressed
            
            self.saveFile(safile)
            return True
            
        else: return False ## User canceled.
            

    def saveFile(self, safile):
        
        dir, fil, ext = fileparse(safile)
            #e only ext needed in most cases here, could replace with os.path.split [bruce 050907 comment]
                    
        if ext == ".mmp" : # Write MMP file
            self.save_mmp_file( safile)

        elif ext == ".pdb": # Write PDB file.
            try:
                writepdb(self.assy, safile)
            except:
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                env.history.message(redmsg( "Problem saving PDB file: " + safile ))
            else:
                self._updateRecentFileList(safile)
                
                self.saved_main_file(safile, fil)
                    #bruce 050907 split out this common code, though it's probably bad design for PDB files (as i commented elsewhere)
                env.history.message( "PDB file saved: " + self.assy.filename )
                    #bruce 050907 moved this after mt_update (which is now in saved_main_file)
        else:
            self.saveSeparateFile( safile)
        return

    def saveSeparateFile( self, safile): #bruce 050908 split this out, reorganized code, revised bug-only history messages
        "Save some aspect of the current part in a separate file, without resetting the current part's changed flag or filename."
        #e later we might add ability to specify *what* part to save (main part, some clipboard part, selection),
        # and/or ability for format to be mmp or pdb.
        # Or (better), this might become a method of a "saveable object" (open file) or a "saveable subobject" (part, selection).
        dir, fil, ext = fileparse(safile)
            #e only ext needed in most cases here, could replace with os.path.split [bruce 050908 comment]
        type = "this" # never used (even if caller passes in unsupported filetype) unless there are bugs in this routine
        saved = True # be optimistic (not bugsafe; fix later by having save methods which return a success code)
        try:
            # all these cases modify type variable, for use only in subsequent messages
            if ext == ".pov":
                type = "POV-Ray"
                writepovfile(self.assy, safile)
            elif ext == ".mdl":
                type = "MDL"
                writemdlfile(self.assy, safile)
            elif ext == ".jpg":
                type = "JPEG"
                image = self.glpane.grabFrameBuffer()
                image.save(safile, "JPEG", 85)
            elif ext == ".png":
                type = "PNG"
                image = self.glpane.grabFrameBuffer()
                image.save(safile, "PNG")
            else: # caller passed in unsupported filetype (should never happen)
                saved = False
                env.history.message(redmsg( "File Not Saved. Unknown extension: " + ext))
        except:
            print_compact_traceback( "error writing file %r: " % safile )
            env.history.message(redmsg( "Problem saving %s file: " % type + safile ))
        else:
            if saved:
                env.history.message( "%s file saved: " % type + safile )
        return

    def save_mmp_file(self, safile): #bruce 050907 split this out of saveFile; maybe some of it should be moved back into caller ###@@@untested
        dir, fil, extjunk = fileparse(safile)
        try:
            tmpname = os.path.join(dir, '~' + fil + '.m~')
            self.assy.writemmpfile(tmpname)
        except:
            #bruce 050419 revised printed error message
            print_compact_traceback( "MWsemantics.py: saveFile(): error writing file [%s]: " % safile )
            env.history.message(redmsg( "Problem saving file: " + safile ))
            
            # If you want to see what was wrong with the MMP file, you
            # can comment this out so you can see what's in
            # the temp MMP file.  Mark 050128.
            if os.path.exists(tmpname):
                os.remove (tmpname) # Delete tmp MMP file
        else:
            self._updateRecentFileList(safile)
            
            if os.path.exists(safile):
                os.remove (safile) # Delete original MMP file
                #bruce 050907 suspects this is never necessary, but not sure;
                # if true, it should be removed, so there is never a time with no file at that filename.
                # (#e In principle we could try just moving it first, and only if that fails, try removing and then moving.)

            os.rename( tmpname, safile) # Move tmp file to saved filename.

            self.saved_main_file(safile, fil)
            env.history.message( "MMP file saved: " + self.assy.filename )
                #bruce 050907 moved this after mt_update (which is now in saved_main_file)
        return

    def saved_main_file(self, safile, fil): #bruce 050907 split this out of mmp and pdb saving code
        """Record the fact that self.assy itself is now saved into (the same or a new) main file
        (and will continue to be saved into that file, until further notice)
        (as opposed to part or all of it being saved into some separate file, with no change in status of main file).
        Do necessary changes (filename, window caption, assy.changed status) and updates, but emit no history message.
        """
        # (It's probably bad design of pdb save semantics for it to rename the assy filename -- it's more like saving pov, etc.
        #  This relates to some bug reports. [bruce 050907 comment])
        # [btw some of this should be split out into an assy method, or more precisely a savable-object method #e]
        self.assy.filename = safile
        self.assy.name = fil
        self.assy.reset_changed() # The file and the part are now the same.
#                self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
        self.update_mainwindow_caption()
        self.mt.mt_update() # since it displays self.assy.name [bruce comment 050907; a guess]
            # [note, before this routine was split out, the mt_update happened after the history message printed by our callers]
        return
        
    def prepareToClose(self): #bruce 050907 split this out of MWsemantics.closeEvent method, added docstring
        """Prepare to close the main window and exit (e.g. ask user whether to save file if necessary).
        If user cancels, or anything else means we should not actually close and exit,
        return False; otherwise return True.
        """
        if not self.assy.has_changed():
            return True
        else:
            rc = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before exiting?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2

            if rc == 0:
                # Save
                isFileSaved = self.fileSave() # Save clicked or Alt+S pressed or Enter pressed.
                ##Huaicai 1/6/05: While in the "Save File" dialog, if user chooses
                ## "Cancel", the "Exit" action should be ignored. bug 300
                if isFileSaved:
                    return True
                else:
                    return False
            elif rc == 1: # Discard
                return True
            else: # Cancel
                return False
        pass
            
    def closeEvent(self,ce): #bruce 050907 split this into two methods, revised docstring
        """slot method, called via File > Exit or clicking X titlebar button"""
        #bruce 090507 comment: this slot method should be moved back to MWsemantics.py.
        shouldEventBeAccepted = self.prepareToClose()
        if shouldEventBeAccepted:
            ce.accept()
            ##self.periodicTable.close()
        else:
            ce.ignore()
            env.history.message("Cancelled exit.") # bruce 050907 added this message
        return

    def fileClose(self):
        
        env.history.message(greenmsg("Close File:"))
        
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
                env.history.message("Changes discarded.")
            elif ret==2: 
                env.history.message("Cancelled.")
                return # Cancel clicked or Alt+C pressed or Escape pressed
        
        if isFileSaved: 
                self.__clear() # leaves glpane.mode as nullmode, as of 050911
                self.glpane.start_using_mode( '$STARTUP_MODE') #bruce 050911: File->Clear sets same mode as app startup does
                self.assy.reset_changed() #bruce 050429, part of fixing bug 413
                self.win_update()
        return

    def fileSetWorkDir(self):
        """Sets working directory"""

        env.history.message(greenmsg("Set Working Directory:"))
        
        wd = globalParms['WorkingDirectory']
        wdstr = "Current Working Directory - [" + wd  + "]"
        wd = QFileDialog.getExistingDirectory( wd, self, "get existing directory", wdstr, 1 )
        
        if not wd:
            env.history.message("Cancelled.")
            return
            
        if wd:
            wd = str(wd)
            wd = os.path.normpath(wd)
            globalParms['WorkingDirectory'] = wd
            
            env.history.message( "Working Directory set to " + wd )

            # bruce 050119: store this in prefs database so no need for ~/.ne1rc
            from preferences import prefs_context
            prefs = prefs_context()
            prefs['WorkingDirectory'] = wd
                
    def __clear(self): #bruce 050911 revised this: leaves glpane.mode as nullmode
        #bruce 050907 comment: this is only called from two file ops in this mixin, so I moved it here from MWsemantics
        # even though its name-mangled name was thereby changed. It should really be given a normal name.
        # Some comments in other files still call it MWsemantics.__clear.
        
        # assyList refs deleted by josh 10/4
        self.assy = assembly(self, "Untitled")
#        self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.name + "]"))
        self.update_mainwindow_caption()
        self.glpane.setAssy(self.assy) # leaves glpane.mode as nullmode, as of 050911
        self.assy.mt = self.mt
        
        ### Hack by Huaicai 2/1 to fix bug 369
        self.mt.resetAssy_and_clear() 

    
    def _updateRecentFileList(self, fileName):
        '''Add the <fileName> into the recent file list '''
        LIST_CAPACITY = 4 #This could be set by user preference, not added yet        
     
        if not __debug__:
            fileName = str(fileName)
        
        if __debug__:
            fileList = self.prefsSetting.readListEntry('recentFiles')[0]
        else:
            fileList = self.prefsSetting.get('recentFiles', [])
        
        if len(fileList) > 0:
           if fileName == fileList[0]:
               return
           else:
               for ii in range(len(fileList)):
                   if fileList[ii] == fileName: ## Put this one at the top
                       del fileList[ii]
                       break
        
        if __debug__:
            fileList.prepend(fileName)
        else:
            fileList.insert(0, fileName)
            
        fileList = fileList[:LIST_CAPACITY]
        
        if __debug__:
            self.prefsSetting.writeEntry('recentFiles', fileList)
        else:
            self.prefsSetting['recentFiles'] = fileList 
        
        self._createRecentFilesList()
        
        

    def _openRecentFile(self, idx):
        '''Slot method when user choose from the recently opened files submenu. '''
        if __debug__:
            fileList = self.prefsSetting.readListEntry('recentFiles')[0]
        else:
            fileList = self.prefsSetting.get('recentFiles', [])
        
        assert idx <= len(fileList)
        
        selectedFile = str(fileList[idx])
        self.fileOpen(selectedFile)
        
        
    def _createRecentFilesList(self):
        '''Dynamically construct the list of rencently opened files submenus '''
        if __debug__:
            fileList = self.prefsSetting.readListEntry('recentFiles')[0]
        else:
            fileList = self.prefsSetting.get('recentFiles', [])
        
        self.recentFilePopupMenu = QPopupMenu(self)
        for ii in range(len(fileList)):
            self.recentFilePopupMenu.insertItem(qApp.translate("Main Window",  "&" + str(ii+1) + "  " + str(fileList[ii]), None), ii)
        
        menuIndex = self.RECENT_FILES_MENU_INDEX
        self.fileMenu.removeItemAt(menuIndex)
        self.fileMenu.insertItem(qApp.translate("Main Window", "Recent Files", None), self.recentFilePopupMenu, menuIndex, menuIndex)
        
        self.connect(self.recentFilePopupMenu, SIGNAL('activated (int)'), self._openRecentFile)
        


    pass # end of class fileSlotsMixin

# end
