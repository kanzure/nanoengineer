# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from icon_utilities import geticon

def setupUi(win):
    
    MainWindow = win
    
    ####Tools > Build Tools Menu Start ######    
    
       
    win.modifyHydrogenateAction = QtGui.QWidgetAction(MainWindow)
    win.modifyHydrogenateAction.setIcon(geticon("ui/actions/Tools/Build Tools/Hydrogenate"))
    win.modifyHydrogenateAction.setObjectName("modifyHydrogenateAction")
    
    win.modifyDehydrogenateAction = QtGui.QWidgetAction(MainWindow)
    win.modifyDehydrogenateAction.setIcon(geticon("ui/actions/Tools/Build Tools/Dehydrogenate"))
    win.modifyDehydrogenateAction.setObjectName("modifyDehydrogenateAction")
    
    win.modifyPassivateAction = QtGui.QWidgetAction(MainWindow)
    win.modifyPassivateAction.setIcon(geticon("ui/actions/Tools/Build Tools/Passivate"))
    win.modifyPassivateAction.setObjectName("modifyPassivateAction")
    
    win.modifyDeleteBondsAction = QtGui.QWidgetAction(MainWindow)
    win.modifyDeleteBondsAction.setIcon(geticon("ui/actions/Tools/Build Tools/Delete_Bonds"))
    win.modifyDeleteBondsAction.setObjectName("modifyDeleteBondsAction")      
    
    win.modifySeparateAction = QtGui.QWidgetAction(MainWindow)
    win.modifySeparateAction.setIcon(geticon("ui/actions/Tools/Build Tools/Separate"))
    win.modifySeparateAction.setObjectName("modifySeparateAction")
        
    win.modifyMergeAction = QtGui.QWidgetAction(MainWindow)
    win.modifyMergeAction.setIcon(geticon(
        "ui/actions/Tools/Build Tools/Combine_Chunks"))
    win.modifyMergeAction.setObjectName("modifyMergeAction")
    
    win.makeChunkFromSelectedAtomsAction = QtGui.QWidgetAction(MainWindow)
    win.makeChunkFromSelectedAtomsAction.setIcon(geticon(
        "ui/actions/Tools/Build Tools/New_Chunk"))
    win.makeChunkFromSelectedAtomsAction.setObjectName("makeChunkFromSelectedAtomsAction")
    
    
    win.modifyAlignCommonAxisAction = QtGui.QWidgetAction(MainWindow)
    win.modifyAlignCommonAxisAction.setIcon(geticon("ui/actions/Tools/Build Tools/AlignToCommonAxis"))
    win.modifyAlignCommonAxisAction.setObjectName("modifyAlignCommonAxisAction")
    
    win.modifyCenterCommonAxisAction = QtGui.QWidgetAction(MainWindow)
    win.modifyCenterCommonAxisAction.setObjectName("modifyCenterCommonAxisAction")
                    
    win.buildToolsMenu.addAction(win.modifyHydrogenateAction)
    win.buildToolsMenu.addAction(win.modifyDehydrogenateAction)
    win.buildToolsMenu.addAction(win.modifyPassivateAction)
    
    win.buildToolsMenu.addSeparator()
    
    win.buildToolsMenu.addAction(win.modifyDeleteBondsAction)
    win.buildToolsMenu.addAction(win.modifySeparateAction)
    win.buildToolsMenu.addAction(win.modifyMergeAction)
        
    win.buildToolsMenu.addSeparator()
    
    win.buildToolsMenu.addAction(win.modifyAlignCommonAxisAction)
    win.buildToolsMenu.addAction(win.modifyCenterCommonAxisAction)
    
    win.buildToolsMenu.addSeparator() 
    
    
 
    ####Tools > Build Tools Menu End######
    
 
    
def retranslateUi(win):
    
    win.buildToolsMenu.setTitle(QtGui.QApplication.translate("MainWindow", "Build Tools", None, QtGui.QApplication.UnicodeUTF8))
    
    #TOOLS > BUILD TOOLS MENU ITEMS
    
    win.modifyHydrogenateAction.setText(QtGui.QApplication.translate("MainWindow", "&Hydrogenate", 
                                                                     None, QtGui.QApplication.UnicodeUTF8))
    win.modifyHydrogenateAction.setIconText(QtGui.QApplication.translate("MainWindow", "Hydrogenate", 
                                                                         None, QtGui.QApplication.UnicodeUTF8))
    win.modifyHydrogenateAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Hydrogenate", 
                                                                        None, QtGui.QApplication.UnicodeUTF8))
    win.modifyHydrogenateAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Shift+H", 
                                                                         None, QtGui.QApplication.UnicodeUTF8))
    win.modifyDehydrogenateAction.setText(QtGui.QApplication.translate("MainWindow", "&Dehydrogenate", 
                                                                       None, QtGui.QApplication.UnicodeUTF8))
    win.modifyDehydrogenateAction.setIconText(QtGui.QApplication.translate("MainWindow", "Dehydrogenate", 
                                                                           None, QtGui.QApplication.UnicodeUTF8))
    win.modifyPassivateAction.setText(QtGui.QApplication.translate("MainWindow", "&Passivate", 
                                                                   None, QtGui.QApplication.UnicodeUTF8))
    win.modifyPassivateAction.setIconText(QtGui.QApplication.translate("MainWindow", "Passivate", 
                                                                       None, QtGui.QApplication.UnicodeUTF8))
    win.modifyPassivateAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Passivate (Ctrl+P)",
                                                                      None, QtGui.QApplication.UnicodeUTF8))
    win.modifyPassivateAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+P", 
                                                                       None, QtGui.QApplication.UnicodeUTF8))
    win.modifyDeleteBondsAction.setText(QtGui.QApplication.translate(
        "MainWindow", "Cut &Bonds",None, QtGui.QApplication.UnicodeUTF8))
    win.modifyDeleteBondsAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Cut Bonds",None, QtGui.QApplication.UnicodeUTF8))
    win.modifyMergeAction.setText(QtGui.QApplication.translate(
        "MainWindow","Combine",None,QtGui.QApplication.UnicodeUTF8))
   
    win.modifyMergeAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow","Merge Selected Chunks",None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.makeChunkFromSelectedAtomsAction.setText(QtGui.QApplication.translate(
        "MainWindow","New Chunk",None,QtGui.QApplication.UnicodeUTF8))

    win.makeChunkFromSelectedAtomsAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow","Create a new chunk for selected atoms",None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.modifySeparateAction.setText(QtGui.QApplication.translate(
        "MainWindow",  "&Separate", None,QtGui.QApplication.UnicodeUTF8))
    win.modifySeparateAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Separate", None, QtGui.QApplication.UnicodeUTF8))
    win.modifyAlignCommonAxisAction.setText(QtGui.QApplication.translate(
        "MainWindow", "Align to &Common Axis",None, 
        QtGui.QApplication.UnicodeUTF8))
    win.modifyAlignCommonAxisAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Align to Common Axis",None, 
        QtGui.QApplication.UnicodeUTF8))
    win.modifyCenterCommonAxisAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Center on Common Axis",None,
        QtGui.QApplication.UnicodeUTF8))        
    
