# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""


The Ui_MoviePropertyManager class defines UI elements for the Property 
Manager of the B{Movie mode}.

@author: Mark, Ninad
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
ninad 2007-05-07 : Converted movie dashboard into movie Property manager
ninad 2007-09-11: Code clean up to use PM module classes

#TODO: Ui_MoviePlayerManager uses some Mainwindow widgets and actions 
#(This is because Movie PM uses most methods originally created for movie 
#dashboard and Movie dashboard defined them this way -- ninad 2007-05-07
"""


import sys

from PyQt4.Qt import Qt

from PM.PM_Dialog        import PM_Dialog
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_Slider        import PM_Slider
from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_SpinBox       import PM_SpinBox
from PM.PM_WidgetRow     import PM_WidgetRow
from PM.PM_ToolButton    import PM_ToolButton

from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton
from PM.PM_Constants     import pmCancelButton

from icon_utilities      import geticon
from NE1ToolBar          import NE1ToolBar


class Ui_MoviePropertyManager(PM_Dialog):
    """
    The Ui_MoviePropertyManager class defines UI elements for the Property 
    Manager of the B{Movie mode}.
    
    @ivar title: The title that appears in the property manager header.
    @type title: str
    
    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str
    
    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """
    
    # The title(s) that appears in the property manager header.
    title = "Play Movie"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The full path to PNG file(s) that appears in the header.
    iconPath = "ui/actions/Simulation/Play_Movie.png"
    
    def __init__(self, parentMode):
        """
        Constructor for the B{Movie} property manager class that defines 
        its UI.
        
        @param parentMode: The parent mode where this Property Manager is used
        @type  parentMode: L{movieMode}        
        """
        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)
        
        self.showTopRowButtons( pmDoneButton | \
                                pmCancelButton | \
                                pmWhatsThisButton)
        
        self.parentMode = parentMode
        self.w = self.parentMode.w
        self.win = self.parentMode.w
        self.o = self.parentMode.o
        self.pw = self.parentMode.pw
        msg = ''
        self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)
    
    def _addGroupBoxes(self):
        """
        Add various group boxes to the Movie Property manager. 
        """     
        self._addMovieControlsGroupBox()
        self._addMovieOptionsGroupBox()
        self._addMovieFilesGroupBox()
            
    def _addMovieControlsGroupBox(self):
        """
        Add Movie Controls groupbox
        """
        self.movieControlsGroupBox = PM_GroupBox(self, 
                                                 title = "Movie Controls"
                                                 )
        self._loadMovieControlsGroupBox(self.movieControlsGroupBox)
        
    
    def _addMovieOptionsGroupBox(self):
        """
        Add Movie Options groupbox
        """
        self.movieOptionsGroupBox = PM_GroupBox(self, 
                                                 title = "Movie Options"
                                                 )
        self._loadMovieOptionsGroupBox(self.movieOptionsGroupBox)
        
    
    def _addMovieFilesGroupBox(self):
        """
        Add Open / Save Movie File groupbox
        """
        self.movieFilesGroupBox = PM_GroupBox(self, 
                                                 title = "Open/Save Movie File"
                                                 )
        self._loadMovieFilesGroupBox(self.movieFilesGroupBox)
    
    def _loadMovieControlsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Movie Controls group box.
        @param inPmGroupBox: The Movie Controls groupbox in the PM
        @type  inPmGroupBox: L{PM_GroupBox} 
        """
        #Movie Slider
        self.w.frameNumberSL = \
            PM_Slider( inPmGroupBox,
                       currentValue = 0,
                       minimum      = 0,
                       maximum      = 999999,
                       label        = 'Current Frame: 0/900'
                     )
        self.w.movieFrameUpdateLabel = self.w.frameNumberSL.labelWidget
        
        #Movie Controls
        
        self.movieButtonsToolBar = NE1ToolBar(inPmGroupBox)
        
        movieActionList = [self.w.movieResetAction,
                           self.w.moviePlayRevActiveAction,
                           self.w.moviePlayRevAction,
                           self.w.moviePauseAction,
                           self.w.moviePlayAction,
                           self.w.moviePlayActiveAction,
                           self.w.movieMoveToEndAction
                           ]
        
        for action in movieActionList:
            self.movieButtonsToolBar.addAction(action)
                
        self.w.moviePlayActiveAction.setVisible(0)
        self.w.moviePlayRevActiveAction.setVisible(0)
        
        WIDGET_LIST = [("PM_", self.movieButtonsToolBar, 0)]
        
        self.moviecontrolsWidgetRow = PM_WidgetRow(inPmGroupBox, 
                                                   widgetList = WIDGET_LIST,
                                                   spanWidth = True)
        
        self.w.movieLoop_checkbox = PM_CheckBox(inPmGroupBox,
                                                text = "Loop",
                                                widgetColumn = 0,
                                                state = Qt.Unchecked) 
        
        #####################DEBUG ONLY STARTS###############################
        if 0:
            #+++++++DEBUG ONLY+++++
            
            # Button list to create a toolbutton row.
            # Format: 
            # - buttonId, 
            # - buttonText , 
            # - iconPath
            # - tooltip
            # - shortcut
            # - column
            MOVIE_CONTROL_BUTTONS = \
                              [ ( "QToolButton", 0, "Reset Movie","", "", 
                                  None, 0),
                                ( "QToolButton", 1,  "Reverse",    "", "", 
                                  None, 1),
                                ( "QToolButton", 2,  "TRIPLE",    "", "", 
                                  None, 2),
                                ( "QToolButton", 3,  "AROMATIC",  "", "", 
                                  None, 3),
                                ( "QToolButton", 4,  "GRAPHITIC", "", "", 
                                  None, 4),
                                ( "QToolButton", 5,  "CUTBONDS",  "", "", 
                                  None, 5)
                              ]
                            
                
            self.movieControlsButtonRow = \
                PM_ToolButtonRow( 
                    inPmGroupBox, 
                    title        = "",
                    buttonList   = MOVIE_CONTROL_BUTTONS,
                    checkedId    = 0,
                    setAsDefault = True )
            
                                                       
            for btn in self.movieControlsButtonRow.buttons():
                btnId = self.movieControlsButtonRow.buttonGroup.id(btn)
                action = bondToolActions[btnId]
                action.setCheckable(True)
                btn.setIconSize(QSize(24,24))
                btn.setDefaultAction(action)
        #####################DEBUG ONLY ENDS################################

    def _loadMovieFilesGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Open/Save Movie Files group box.
        @param inPmGroupBox: The Open/Save Movie Files groupbox in the PM
        @type  inPmGroupBox: L{PM_GroupBox} 
        """
        
        for action in self.w.fileOpenMovieAction, self.w.fileSaveMovieAction:
            btn = PM_ToolButton(inPmGroupBox,
                                text = str(action.text()),
                                spanWidth = True)
            btn.setDefaultAction(action)
            btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
          
    def _loadMovieOptionsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Movie Options group box.
        @param inPmGroupBox: The Movie Options groupbox in the PM
        @type  inPmGroupBox: L{PM_GroupBox} 
        """
        
        self.w.frameNumberSB = PM_SpinBox(inPmGroupBox,
                                          label         =  "Go To Frame:",
                                          labelColumn   =  0,
                                          value         =  0,
                                          minimum       =  1,
                                          maximum       =  999999)
        
        self.w.skipSB = PM_SpinBox(inPmGroupBox,
                                          label         =  "Skip:",
                                          labelColumn   =  0,
                                          value         =  0,
                                          minimum       =  1,
                                          maximum       =  9999,
                                          suffix        = ' Frame(s)')