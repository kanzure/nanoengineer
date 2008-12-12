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

from widgets.prefs_widgets import connect_checkbox_with_boolean_pref
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL
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

from command_support.Command_PropertyManager import Command_PropertyManager
from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_OrderDna_PropertyManager


def writeDnaOrderFile(fileName, 
                      assy, 
                      numberOfBases, 
                      numberOfUnassignedBases, 
                      dnaSequence):
    """
    Writes a DNA Order file in comma-separated value (CSV) format.
    
    @param fileName: The full path of the DNA order file.
    @param assy: The assembly.
    @param numberOfBase: The number of bases.
    @param numberOfUnassignedBases: The number of unassigned (i.e. X) bases.
    @param  dnaSequence: The dnaSequence string to be written to the file.
    @see: self.orderDna
    """
    
    #Create Header
    date_header = "#NanoEngineer-1 DNA Order Form created on %s\n" \
               % time.strftime("%Y-%m-%d at %H:%M:%S")
    
    if assy.filename:
        mmpFileName = "[" + os.path.normpath(assy.filename) + "]"
    else:
        mmpFileName = "[" + assy.name + "]" + \
                    " ( The mmp file was probably not saved when the "\
                    " sequence was written)"
    
    fileNameInfo_header = "#This sequence is created for file '%s'\n" \
                        % mmpFileName
    
    numberOfBases_header = "#Total number of bases: %d\n" % numberOfBases
    
    unassignedBases_header = ""
    if numberOfUnassignedBases:
        unassignedBases_header = \
            "#WARNING: This order includes %d unassigned (i.e. \"X\") bases.\n"\
            % numberOfUnassignedBases
    
    info_header = "#This file is written in comma-separated value (CSV) format. "\
                "Open with Excel or any other program that supports CSV format.\n"
    
    column_header = "Name,Length,Sequence,Notes\n"
    
    file_header = date_header \
                + fileNameInfo_header \
                + numberOfBases_header \
                + unassignedBases_header \
                + info_header \
                + "\n" \
                + column_header
    
    # Write file
    f = open(fileName,'w')
    f.write(file_header)
    f.write(dnaSequence)
    f.close()
    return


_superclass = Command_PropertyManager
class OrderDna_PropertyManager(Command_PropertyManager):
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

    title         =  "Order DNA"
    pmName        =  title
    iconPath      =  "ui/actions/Command Toolbar/BuildDna/OrderDna.png"
    
    def __init__( self, command ):
        """
        Constructor for the property manager.
        """
        
        _superclass.__init__(self, command)
        
        self.assy = self.win.assy

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
        
        self.update_includeStrands() # Updates the message box.
        return
        
        
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
        return
       
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
                         label  =  "Total nucleotides:",
                         text   = str(self.getNumberOfBases()))
        self.numberOfBasesLineEdit.setEnabled(False)
        
        self.numberOfXBasesLineEdit  = \
            PM_LineEdit( pmGroupBox,
                         label  =  "Unassigned:",
                         text   = str(self.getNumberOfBases(unassignedOnly = True)))
        self.numberOfXBasesLineEdit.setEnabled(False)
        
        self.viewDnaOrderFileButton = \
            PM_PushButton( pmGroupBox,
                           label     = "",
                           text      = "View DNA Order File...",
                           spanWidth = True)
        return
    
    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.
        """
        whatsThis_OrderDna_PropertyManager(self)
        return
    
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
    
    def getNumberOfBases(self, selectedOnly = False, unassignedOnly = False):
        """
        Returns the number of bases count for all the DNA strands in the 
        current part, or only the selected strand if I{selectedOnly} is True.
        
        @param selectedOnly: If True, return only the number of bases in the
                             selected DNA strands.
        @type  selectedOnly: bool
        
        @param unassignedOnly: If True, return only the number of unassigned
                               bases (i.e. base letters = X).
        @type  unassignedOnly: bool
        """
        dnaSequenceString = ''
        selectedOnly = self.includeStrandsComboBox.currentIndex()
        strandList = self.getAllDnaStrands(selectedOnly)
        
        for strand in strandList:
            strandSequenceString = str(strand.getStrandSequence())
            dnaSequenceString += strandSequenceString
        
        if unassignedOnly:
            return dnaSequenceString.count("X")
        
        return len(dnaSequenceString)
    
    def _update_UI_do_updates(self):
        """
        Overrides superclass method.
        """
        self.update_includeStrands()
        return
        
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
                strandLength = str(len(strandSequenceString)) + separator
                dnaSequenceString = dnaSequenceString + strandLength + strandSequenceString
                
            dnaSequenceString = dnaSequenceString + "\n"
            
        return dnaSequenceString
        
    def viewDnaOrderFile(self, openFileInEditor = True):
        """
        Writes a DNA Order file in comma-separated values (CSV) format 
        and opens it in a text editor.

        The user must save the file to a permanent location using the 
        text editor.

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
                              self.getNumberOfBases(),
                              self.getNumberOfBases(unassignedOnly = True),
                              dnaSequence)      

            if openFileInEditor:
                open_file_in_editor(temporaryFile)
                
        return

    def update_includeStrands(self, ignoreVal = 0):
        """
        Slot method for "Include (strands)" combobox.
        """
        
        idx = self.includeStrandsComboBox.currentIndex()
        
        includeType = ["model", "selection"]
        
        _numberOfBases = self.getNumberOfBases()
        self.numberOfBasesLineEdit.setText(str(_numberOfBases) + " bases")
        
        _numberOfXBases = self.getNumberOfBases(unassignedOnly = True)
        self.numberOfXBasesLineEdit.setText(str(_numberOfXBases) + " bases")
        
        # Make the background color red if there are any unassigned bases.
        if _numberOfXBases:
            self.numberOfXBasesLineEdit.setStyleSheet(\
                "QLineEdit {"\
                "background-color: rgb(255, 0, 0)"\
                "}")
        else:
            self.numberOfXBasesLineEdit.setStyleSheet(\
                "QLineEdit {"\
                "background-color: rgb(255, 255, 255)"\
                "}")
        
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
        return
