# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""

The Ui_MoviePropertyManager class defines UI elements for the Property 
Manager of the B{Movie mode}.

@author: Mark, Ninad
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
ninad 2007-05-07 : Converted movie dashboard into movie Property manager
ninad 2007-09-11: Code clean up to use PM module classes

#TODO: Ui_MoviePlayerManager uses some Mainwindow widgets and actions 
#(This is because Movie PM uses most methods originally created for movie 
#dashboard and Movie dashboard defined them this way -- ninad 2007-05-07
"""

from PyQt4               import QtGui
from PyQt4.Qt            import Qt
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_Slider        import PM_Slider
from PM.PM_SpinBox       import PM_SpinBox
from PM.PM_WidgetRow     import PM_WidgetRow
from PM.PM_ToolButton    import PM_ToolButton

from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON

from widgets.NE1ToolBar import NE1ToolBar
from utilities.icon_utilities import geticon
from command_support.Command_PropertyManager import Command_PropertyManager

_superclass = Command_PropertyManager
class Ui_MoviePropertyManager(Command_PropertyManager):
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
    iconPath = "ui/actions/Simulation/PlayMovie.png"

    def __init__(self, command):
        """
        Constructor for the B{Movie} property manager class that defines 
        its UI.

        @param command: The parent mode where this Property Manager is used
        @type  command: L{movieMode}        
        """
        _superclass.__init__(self, command)

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_CANCEL_BUTTON | \
                                PM_WHATS_THIS_BUTTON)


        msg = ''
        self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)

    def _addGroupBoxes(self):
        """
        Add various group boxes to the Movie Property manager. 
        """
        self._createAllActionWidgets()
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
        self.frameNumberSlider = \
            PM_Slider( inPmGroupBox,
                       currentValue = 0,
                       minimum      = 0,
                       maximum      = 999999,
                       label        = 'Current Frame: 0/900'
                       )

        self.movieFrameUpdateLabel = self.frameNumberSlider.labelWidget

        #Movie Controls

        self.movieButtonsToolBar = NE1ToolBar(inPmGroupBox)

        _movieActionList = [self.movieResetAction,
                            self.moviePlayRevActiveAction,
                            self.moviePlayRevAction,
                            self.moviePauseAction,
                            self.moviePlayAction,
                            self.moviePlayActiveAction,
                            self.movieMoveToEndAction
                            ]

        for _action in _movieActionList:
            self.movieButtonsToolBar.addAction(_action)

        self.moviePlayActiveAction.setVisible(0)
        self.moviePlayRevActiveAction.setVisible(0)

        WIDGET_LIST = [("PM_", self.movieButtonsToolBar, 0)]

        self.moviecontrolsWidgetRow = PM_WidgetRow(inPmGroupBox, 
                                                   widgetList = WIDGET_LIST,
                                                   spanWidth = True)

        self.movieLoop_checkbox = PM_CheckBox(inPmGroupBox,
                                              text = "Loop",
                                              widgetColumn = 0,
                                              state = Qt.Unchecked)

    def _loadMovieOptionsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Movie Options group box.
        @param inPmGroupBox: The Movie Options groupbox in the PM
        @type  inPmGroupBox: L{PM_GroupBox} 
        """

        self.frameNumberSpinBox = PM_SpinBox(inPmGroupBox,
                                             label         =  "Go To Frame:",
                                             labelColumn   =  0,
                                             value         =  0,
                                             minimum       =  1,
                                             maximum       =  999999)

        self.frameSkipSpinBox = PM_SpinBox(inPmGroupBox,
                                           label         =  "Skip:",
                                           labelColumn   =  0,
                                           value         =  0,
                                           minimum       =  1,
                                           maximum       =  9999,
                                           suffix        = ' Frame(s)')

    def _loadMovieFilesGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Open/Save Movie Files group box.
        @param inPmGroupBox: The Open/Save Movie Files groupbox in the PM
        @type  inPmGroupBox: L{PM_GroupBox} 
        """

        for action in self.fileOpenMovieAction, self.fileSaveMovieAction:
            btn = PM_ToolButton(inPmGroupBox,
                                text = str(action.text()),
                                spanWidth = True)
            btn.setDefaultAction(action)
            btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

    def _createAllActionWidgets(self):
        """
        Creates all the QAction widgets that will end up as buttons in the PM.
        """
        self.movieResetAction = QtGui.QAction(self)
        self.movieResetAction.setObjectName("movieResetAction")
        self.movieResetAction.setIcon(
            geticon("ui/actions/Properties Manager/Movie_Reset.png"))

        self.moviePlayRevActiveAction = QtGui.QAction(self)
        self.moviePlayRevActiveAction.setObjectName("moviePlayRevActiveAction")
        self.moviePlayRevActiveAction.setIcon(
            geticon("ui/actions/Properties Manager/Movie_Play_Reverse_Active.png"))

        self.moviePlayRevAction = QtGui.QAction(self)
        self.moviePlayRevAction.setObjectName("moviePlayRevAction")
        self.moviePlayRevAction.setIcon(
            geticon("ui/actions/Properties Manager/Movie_Play_Reverse.png"))

        self.moviePauseAction = QtGui.QAction(self)
        self.moviePauseAction.setObjectName("moviePauseAction")
        self.moviePauseAction.setIcon(
            geticon("ui/actions/Properties Manager/Movie_Pause.png"))

        self.moviePlayAction = QtGui.QAction(self)
        self.moviePlayAction.setObjectName("moviePlayAction")
        self.moviePlayAction.setVisible(True)
        self.moviePlayAction.setIcon(
            geticon("ui/actions/Properties Manager/Movie_Play_Forward.png"))

        self.moviePlayActiveAction = QtGui.QAction(self)
        self.moviePlayActiveAction.setObjectName("moviePlayActiveAction")
        self.moviePlayActiveAction.setIcon(
            geticon("ui/actions/Properties Manager/Movie_Play_Forward_Active.png"))

        self.movieMoveToEndAction = QtGui.QAction(self)
        self.movieMoveToEndAction.setObjectName("movieMoveToEndAction")
        self.movieMoveToEndAction.setIcon(
            geticon("ui/actions/Properties Manager/Movie_Move_To_End.png"))

        self.fileOpenMovieAction = QtGui.QAction(self)
        self.fileOpenMovieAction.setObjectName("fileOpenMovieAction")
        self.fileOpenMovieAction.setIcon(
            geticon("ui/actions/Properties Manager/Open.png"))

        self.fileSaveMovieAction = QtGui.QAction(self)
        self.fileSaveMovieAction.setObjectName("fileSaveMovieAction")
        self.fileSaveMovieAction.setIcon(
            geticon("ui/actions/Properties Manager/Save.png"))

        self.fileSaveMovieAction.setText(
            QtGui.QApplication.translate("MainWindow", 
                                         "Save Movie File...", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))

        self.fileOpenMovieAction.setText(
            QtGui.QApplication.translate("MainWindow", 
                                         "Open Movie File...", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))

        # This isn't currently in the PM. It's connected and ready to go.
        self.movieInfoAction = QtGui.QAction(self)
        self.movieInfoAction.setObjectName("movieInfoAction")
        self.movieInfoAction.setIcon(
            geticon("ui/actions/Properties Manager/Movie_Info.png"))



    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.  
        """
        from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_MoviePropertyManager
        whatsThis_MoviePropertyManager(self)

    def _addToolTipText(self):
        """
        Tool Tip text for widgets in this Property Manager.  
        """
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_MoviePropertyManager
        ToolTip_MoviePropertyManager(self)