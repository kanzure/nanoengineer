# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_WhatsThisText.py

@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

"""

##from DnaDuplexPropertyManager import DnaDuplexPropertyManager

def whatsThis_DnaDuplexPropertyManager(propMgr):
    """
    Whats this text for the DnaDuplexProperty Manager
    @see: B{DnaDuplexPropertyManager._addWhatsThisText}
    """
    
    
    #TODO: If we import DnaDuplexPropertyManager here, that will create an 
    #import cycle. so don't do the following isinstance check yet. Need to 
    #figureout a better way of doing this -- Ninad 2007-12-20
    ##assert isinstance(propMgr, DnaDuplexPropertyManager)
    
    txt_conformationComboBox = "<b>Conformation</b> <p>DNA exists in "\
                                 "several possible conformations, with A-DNA, "\
                                 "B-DNA, and Z-DNA being the most common. <br>"\
                                 "Only B-DNA is currently supported in "\
                                 "NanoEngineer-1.</p>"
    
    if hasattr(propMgr, 'conformationComboBox'):
        propMgr.conformationComboBox.setWhatsThis(txt_conformationComboBox)
    
    
    
    
        