#Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
PM_PartLib.py

The PM_PartLib class provides a groupbox that contains the partlib (any user
specified directory). The parts from the partlib can be pasted into the 3D
workspace. The selected item in this list is shown by its elementViewer
(an instance of L{PM_PreviewGroupBox}). The object being previewed can then be
deposited into the 3D workspace.

@author: Huaicai, Mark, Ninad, Bruce
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

The Partlib existed as a tab in the MMKit of Build Atoms Mode. (MMKit has been
deprecated since 2007-08-29.)

ninad 2007-09-06: Created.
"""
import os
from utilities import debug_flags

from utilities.constants import diTrueCPK
from graphics.widgets.ThumbView import MMKitView
from model.assembly import Assembly
from files.mmp.files_mmp import readmmp

from PM.PM_GroupBox    import PM_GroupBox
from PM.PM_TreeView    import PM_TreeView

class PM_PartLib(PM_GroupBox):
    """
    The PM_PartLib class provides a groupbox containing a partlib directory
    The selected part in this list is shown by its elementViewer
    (an instance of L{PM_PreviewGroupBox})
    The part being previewed can then be deposited into the 3D workspace.
    """
    def __init__(self,
                 parentWidget,
                 title = 'Part Library',
                 win   = None,
                 elementViewer = None
                 ):
        self.w = win
        self.elementViewer = elementViewer
        # piotr 080410 changed diTUBES to diTrueCPK
        self.elementViewer.setDisplay(diTrueCPK)
        self.partLib = None
        self.newModel = None

        PM_GroupBox.__init__(self, parentWidget, title)

        self._loadPartLibGroupBox()

    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot
                          method.
        @type  isConnect: boolean
        """
        ##if isConnect:
        ##    change_connect = self.w.connect
        ##else:
        ##    change_connect = self.w.disconnect

        #Following doesn't work for some reasons so this call is disabled.
        #Instead , see PM_TreeView.mouseReleaseEvent where self.partChanged is
        #called.
        ##change_connect(self.partLib,
        ##               SIGNAL("selectionChanged(QItemSelection *,\
        ##               QItemSelection *)"),
        ##               self.partChanged)
        pass


    def _loadPartLibGroupBox(self):
        """
        """
        self.partLib = PM_TreeView(self)
        self.gridLayout.addWidget(self.partLib)
        #Append to the widget list. This is important for expand -collapse
        #functions (of the groupbox) to work properly.
        self._widgetList.append(self.partLib)

    def _updateElementViewer(self, newModel = None):
        """
        Update the view of L{self.elementViewer}
        @param newModel: The model correseponding to the item selected
                         in L{self.clipboardListWidget}.
        @type  newModel: L{molecule} or L{Group}
        """
        if not self.elementViewer:
            return

        assert isinstance(self.elementViewer, MMKitView)

        self.elementViewer.resetView()
        if newModel:
            self.elementViewer.updateModel(newModel)

    def partChanged(self, selectedItem):
        """
        Method called when user changed the partlib browser tree.

        @param selectedItem: Item currently selected in the L{self.partLib}
        @type  selectedItem: L{self.partLib.FileItem}

        @attention: This is called in the L{PM_TreeView.mouseReleaseEvent}. The
        'selectionChanged' signal for self.partLib apparently was not emitted
        so that code has been removed.
        """
        #Copying some old code from deprecated MMKit.py -- ninad 2007-09-06
        item = selectedItem
        self.newModel = None
        if isinstance(item, self.partLib.FileItem):
            mmpFile = str(item.getFileObj())
            if os.path.isfile(mmpFile):
                self.newModel = \
                    Assembly(self.w,
                             os.path.normpath(mmpFile),
                             run_updaters = True # desirable for PartLib [bruce 080403]
                         )
                self.newModel.set_glpane(self.elementViewer) # sets its .o and .glpane
                readmmp(self.newModel, mmpFile)
                self.newModel.update_parts() #k not sure if needed after readmmp
                self.newModel.checkparts()
                if self.newModel.shelf.members:
                    for m in self.newModel.shelf.members[:]:
                        m.kill() #k guess about a correct way to handle them
                    self.newModel.update_parts() #k probably not needed
                    self.newModel.checkparts() #k probably not needed

        self._updateElementViewer(self.newModel)



