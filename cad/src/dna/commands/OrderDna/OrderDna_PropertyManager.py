# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
OrderDna_PropertyManager.py

 The OrderDna_PropertyManager class provides a Property Manager 
    for the B{Order Dna} command on the flyout toolbar in the 
    Build > Dna mode. 

@author: Mark
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""
import os, time

from widgets.DebugMenuMixin import DebugMenuMixin
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL
from PM.PM_Dialog   import PM_Dialog
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_LineEdit import PM_LineEdit
from PM.PM_PushButton import PM_PushButton
from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from utilities.prefs_constants import assignColorToBrokenDnaStrands_prefs_key
from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
from platform_dependent.PlatformDependent import open_file_in_editor

from dna.model.DnaStrand import DnaStrand

#debug flag to keep signals always connected
from utilities.GlobalPreferences import KEEP_SIGNALS_ALWAYS_CONNECTED

def writeDnaOrderFile(fileName, assy, dnaSequence):
    """
    Open a temporary file and write the specified Dna sequence into it.
    
    @param fileName: The full path of the temporary file to be opened
    @param assy: The assembly.
    @param  dnaSequence: The dnaSequence string to be written to the file.
    @see: self.orderDna
    """
    
    #Create Header
    headerString = '#NanoEngineer-1 DNA Order Form created on: '
    timestr = "%s\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
    
    if assy.filename:
        mmpFileName = "[" + os.path.normpath(assy.filename) + "]"
    else:
        mmpFileName = "[" + assy.name + "]" + \
                    " ( The mmp file was probably not saved when the "\
                    " sequence was written)"
    
    fileNameInfo_header = "#This sequence is created for file '%s\n\n'" \
                        % mmpFileName
    
    headerString = headerString + timestr + fileNameInfo_header
    
    f = open(fileName,'w')             
    # Write header
    f.write(headerString)
    f.write("Name,Sequence,Notes\n") # Per IDT's Excel format.
    f.write(dnaSequence)

class OrderDna_PropertyManager( PM_Dialog, DebugMenuMixin ):
    """
    The OrderDna_PropertyManager class provides a Property Manager 
    for the B{Order Dna} command on the flyout toolbar in the 
    Build > Dna mode. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Order Dna"
    pmName        =  title
    iconPath      =  "ui/actions/Command Toolbar/Order_DNA.png"
    
    def __init__( self, command ):
        """
        Constructor for the property manager.
        """

        self.command = command
        self.w = self.command.w
        self.win = self.command.w
        self.pw = self.command.pw        
        self.o = self.win.glpane
        self.assy = self.win.assy
                    
        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)
        
        DebugMenuMixin._init1( self )

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
        
        self.update_includeStrands() # Updates the message box.
        
        if KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)
       
        ##if self.getNumberOfBases():
            ##msg = "Click on <b>View DNA Order File...</b> to preview a "\
                ##"DNA order for all DNA strands in the current model."
        ##else:
            ##msg = "<font color=red>There is no DNA in the current model."
        ##self.updateMessage(msg)
        
        
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect 
        
        change_connect( self.viewDnaOrderFileButton,
                        SIGNAL("clicked()"), 
                        self.viewDnaOrderFile)
        
        change_connect( self.includeStrandsComboBox,
                      SIGNAL("activated(int)"),
                      self.update_includeStrands )
        
    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """      
        self.win.toolsDone()
        
    def show(self):
        """
        Shows the Property Manager. Overrides PM_Dialog.show.
        """
        PM_Dialog.show(self)
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(isConnect = True)

    def close(self):
        """
        Closes the Property Manager. Overrides PM_Dialog.close.
        """
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(False)
        PM_Dialog.close(self)
    
    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """        
        self._pmGroupBox1 = PM_GroupBox( self, title = "Options" )
        self._loadGroupBox1( self._pmGroupBox1 )
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        
        includeStrandsChoices = ["All strands in model",
                                 "Selected strands only"]
        
        self.includeStrandsComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Include strands:", 
                         choices       =  includeStrandsChoices,
                         setAsDefault  =  True)
        
        self.numberOfBasesLineEdit  = \
            PM_LineEdit( pmGroupBox,
                         label  =  "Number of bases:",
                         text   = str(self.getNumberOfBases()))
        self.numberOfBasesLineEdit.setEnabled(False)
        
        self.viewDnaOrderFileButton = \
            PM_PushButton( pmGroupBox,
                           label     = "",
                           text      = "View DNA Order File...",
                           spanWidth = True)
    
    def _addWhatsThisText( self ):
        """
        What's This text for widgets in the DNA Property Manager.  
        """
        pass
                
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the DNA Property Manager.  
        """
        pass
    
    # Ask Bruce where this should live (i.e. class Part?) --Mark
    def getAllDnaStrands(self, selectedOnly = False):
        """
        Returns a list of all the DNA strands in the current part, or only
        the selected strands if I{selectedOnly} is True.
        
        @param selectedOnly: If True, return only the selected DNA strands.
        @type  selectedOnly: bool
        """
        
        dnaStrandList = []
         
        def func(node):
            if isinstance(node, DnaStrand):
                if selectedOnly:
                    if node.picked:
                        dnaStrandList.append(node)
                else:
                    dnaStrandList.append(node)
                    
        self.win.assy.part.topnode.apply2all(func)
        
        return dnaStrandList
    
    def getNumberOfBases(self, selectedOnly = False):
        """
        Returns the number of bases count for all the DNA strands in the 
        current part, or only the selected strand if I{selectedOnly} is True.
        
        @param selectedOnly: If True, return only the selected DNA strands.
        @type  selectedOnly: bool
        """
        dnaSequenceString = ''
        selectedOnly = self.includeStrandsComboBox.currentIndex()
        strandList = self.getAllDnaStrands(selectedOnly)
        
        for strand in strandList:
            strandSequenceString = str(strand.getStrandSequence())
            dnaSequenceString += strandSequenceString
            
        return len(dnaSequenceString)
        
    def getDnaSequence(self, format = 'CSV'):
        """
        Return the complete Dna sequence information string (i.e. all strand 
        sequences) in the specified format. 
        
        @return: The Dna sequence string
        @rtype: string
        
        """
        if format == 'CSV': #comma separated values.
            separator = ','
            
        dnaSequenceString = ''
        selectedOnly = self.includeStrandsComboBox.currentIndex()
        strandList = self.getAllDnaStrands(selectedOnly)
        
        for strand in strandList:
            dnaSequenceString = dnaSequenceString + strand.name + separator
            strandSequenceString = str(strand.getStrandSequence())
            if strandSequenceString: 
                strandSequenceString = strandSequenceString.upper()
                dnaSequenceString = dnaSequenceString + strandSequenceString
                
            dnaSequenceString = dnaSequenceString + "\n"
            
        return dnaSequenceString
        
    def viewDnaOrderFile(self, openFileInEditor = True):
        """
        Opens a text editor and loads a temporary text file containing all the 
        DNA strand names and their sequences in the current DNA object. It will
        look something like this: 

        Strand1,ATCAGCTACGCATCGCT
        Strand2,TAGTCGATGCGTAGCGA
        ...
        Strandn, ...

        The user can then save the file to a permanent location using the 
        text editor the file is loaded (and displayed) in.

        @see: Ui_DnaFlyout.orderDnaCommand
        @see: writeDnaOrderFile()
        @TODO: assy.getAllDnaObjects(). 
        """
        dnaSequence = self.getDnaSequence(format = 'CSV')

        if dnaSequence: 
            tmpdir = find_or_make_Nanorex_subdir('temp')
            fileBaseName = 'DnaOrder'
            temporaryFile = os.path.join(tmpdir, "%s.csv" % fileBaseName)            
            writeDnaOrderFile(temporaryFile, 
                              self.assy,
                              dnaSequence)      

            if openFileInEditor:
                open_file_in_editor(temporaryFile)

    def update_includeStrands(self, ignoreVal = 0):
        """
        Slot method for "Include (strands)" combobox.
        """
        
        idx = self.includeStrandsComboBox.currentIndex()
        
        includeType = ["model", "selection"]
        
        _numberOfBases = self.getNumberOfBases()
        self.numberOfBasesLineEdit.setText(str(_numberOfBases))
        
        if _numberOfBases > 0:
            self.viewDnaOrderFileButton.setEnabled(True)
            msg = "Click on <b>View DNA Order File...</b> to preview a " \
                "DNA order for all DNA strands in the current %s." \
                % includeType[idx]
        else:
            self.viewDnaOrderFileButton.setEnabled(False)
            msg = "<font color=red>" \
                "There are no DNA strands in the current %s." \
                % includeType[idx]
                
        self.updateMessage(msg)
            