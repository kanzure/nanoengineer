# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
selectMode.py -- the default mode for Atom's main model view.

$Id$
"""

from modes import *
from chunk import molecule
import env

# wware 060124  Do not commit this file with this flag set to True.
# This is a convenient way to embed Pyrex/OpenGL unit tests into the cad code.
TEST_PYREX_OPENGL = False

# Values for selSense. DO NOT CHANGE THESE VALUES. They correspond to
# the <logic> values used in pickrect() and pickline() in shapes.py.  mark 060205.
SUBTRACT_FROM_SELECTION = 0
ADD_TO_SELECTION = 1
START_NEW_SELECTION = 2

def do_what_MainWindowUI_should_do(w):
    '''This creates the Select Atoms (not the Select Chunks) dashboard .
    '''
     
    w.selectAtomsDashboard.clear()

    w.depositAtomLabel = QLabel(w.selectAtomsDashboard,"Select Atoms")
    w.depositAtomLabel.setText(" Select Atoms ")
    w.selectAtomsDashboard.addSeparator()

    ## Kludge to make it work, it's really not good, may need to rework it later. Huaicai 8/10/05
    #w.filterCheckBox = QCheckBox(" Select Only : ", w.selectAtomsDashboard)
    #w.filterCheckBox.hide()
    #QToolTip.add(w.filterCheckBox, qApp.translate("MainWindow","Selection Filter", None))
    selectLabel = QLabel(w.selectAtomsDashboard, "Select:")
    selectLabel.setText("Select: ")
    
    w.elemFilterComboBox = QComboBox(0,w.selectAtomsDashboard, "elemFilterComboBox")
    
    w.selectConnectedAction.addTo(w.selectAtomsDashboard)
    w.selectDoublyAction.addTo(w.selectAtomsDashboard)
    
    w.selectAtomsDashboard.addSeparator()

    transmute2Label = QLabel(w.selectAtomsDashboard, "Transmute_to:")
    transmute2Label.setText("Transmute to: ")
    w.transmute2ComboBox = QComboBox(0,w.selectAtomsDashboard, "transmute2ComboBox")
    w.connect(w.transmute2ComboBox, SIGNAL("activated(int)"), w.transmuteElementChanged)

    w.atomSelect_hybridComboBox = QComboBox(0, w.selectAtomsDashboard, "hybridComboBox") 
    # Set the width of the hybrid drop box.  Mark 050810.
    width = w.hybridComboBox.fontMetrics().width(" sp2(graphitic) ")
    w.atomSelect_hybridComboBox.setMinimumSize ( QSize (width, 0) )

    w.transmuteButton = QPushButton("Transmute", w.selectAtomsDashboard)
    QToolTip.add(w.transmuteButton, qApp.translate("MainWindow","Transmute Selected Atoms", None))
                 
    w.transmuteCheckBox = QCheckBox(" Force to Keep Bonds", w.selectAtomsDashboard)
    QToolTip.add(w.transmuteCheckBox, qApp.translate("MainWindow","Check to keep bonds when transmute.", None))
    w.modifySetElementAction.setEnabled(False) #addTo(w.selectAtomsDashboard)

    w.selectAtomsDashboard.addSeparator()
    w.toolsDoneAction.addTo(w.selectAtomsDashboard)
    w.selectAtomsDashboard.setLabel("Select Atoms")

    w.elemFilterComboBox.clear()
    # WARNING:
    # these are identified by *position*, not by their text, using corresponding entries in eCCBtab1;
    # this is done by win.elemChange even though nothing but depositMode calls that;
    # the current element is stored in win.Element (as an atomic number ###k).
    # All this needs cleanup so it's safer to modify this and so atomtype can sometimes be included.
    # Both eCCBtab1 and eCCBtab2 are set up and used in MWsemantics but should be moved here,
    # or perhaps with some part moved into elements.py if it ought to share code with elementSelector.py
    # and elementColors.py (though it doesn't now).
    w.elemFilterComboBox.insertItem("All Elements")
    w.elemFilterComboBox.insertItem("Hydrogen")
    w.elemFilterComboBox.insertItem("Helium")
    w.elemFilterComboBox.insertItem("Boron")
    w.elemFilterComboBox.insertItem("Carbon") # will change to two entries, Carbon(sp3) and Carbon(sp2) -- no, use separate combobox
    w.elemFilterComboBox.insertItem("Nitrogen")
    w.elemFilterComboBox.insertItem("Oxygen")
    w.elemFilterComboBox.insertItem("Fluorine")
    w.elemFilterComboBox.insertItem("Neon")
    w.elemFilterComboBox.insertItem("Aluminum")
    w.elemFilterComboBox.insertItem("Silicon")
    w.elemFilterComboBox.insertItem("Phosphorus")
    w.elemFilterComboBox.insertItem("Sulfur")
    w.elemFilterComboBox.insertItem("Chlorine")
    w.elemFilterComboBox.insertItem("Argon")
    w.elemFilterComboBox.insertItem("Germanium")
    w.elemFilterComboBox.insertItem("Arsenic")
    w.elemFilterComboBox.insertItem("Selenium")
    w.elemFilterComboBox.insertItem("Bromine")
    w.elemFilterComboBox.insertItem("Krypton")
    #w.elemFilterComboBox.insertItem("Antimony")
    #w.elemFilterComboBox.insertItem("Tellurium")
    #w.elemFilterComboBox.insertItem("Iodine")
    #w.elemFilterComboBox.insertItem("Xenon")
    
    
    w.transmute2ComboBox.clear()
    w.transmute2ComboBox.insertItem("Hydrogen")
    w.transmute2ComboBox.insertItem("Helium")
    w.transmute2ComboBox.insertItem("Boron")
    w.transmute2ComboBox.insertItem("Carbon") # will change to two entries, Carbon(sp3) and Carbon(sp2) -- no, use separate combobox
    w.transmute2ComboBox.insertItem("Nitrogen")
    w.transmute2ComboBox.insertItem("Oxygen")
    w.transmute2ComboBox.insertItem("Fluorine")
    w.transmute2ComboBox.insertItem("Neon")
    w.transmute2ComboBox.insertItem("Aluminum")
    w.transmute2ComboBox.insertItem("Silicon")
    w.transmute2ComboBox.insertItem("Phosphorus")
    w.transmute2ComboBox.insertItem("Sulfur")
    w.transmute2ComboBox.insertItem("Chlorine")
    w.transmute2ComboBox.insertItem("Argon")
    w.transmute2ComboBox.insertItem("Germanium")
    w.transmute2ComboBox.insertItem("Arsenic")
    w.transmute2ComboBox.insertItem("Selenium")
    w.transmute2ComboBox.insertItem("Bromine")
    w.transmute2ComboBox.insertItem("Krypton")
    
    from whatsthis import create_whats_this_descriptions_for_selectAtomsMode
    create_whats_this_descriptions_for_selectAtomsMode(w)


    
class selectMode(basicMode):
    "the default mode of GLPane"
    
    # class constants
    backgroundColor = 189/255.0, 228/255.0, 238/255.0
    gridColor = (0.0, 0.0, 0.6)

    # default initial values
    savedOrtho = 0

    jigSelectionEnabled = True
    
    selCurve_List = []
        # <selCurve_List> contains a list of points used to draw the selection curve.  The points lay in the 
        # plane parallel to the screen, just beyond the front clipping plane, so that they are always
        #  inside the clipping volume.
    selArea_List = []
        # <selArea_List> contains a list of points that define the selection area.  The points lay in 
        # the plane parallel to the screen and pass through the center of the view.  The list
        # is used by pickrect() and pickline() to make the selection.
    selShape = SELSHAPE_RECT
        # <selShape> the current selection shape.


    #def __init__(self, glpane):
    #    """The initial function is called only once for the whole program """
    #    basicMode.__init__(self, glpane)
    #    self.jigSelectionEnabled = True
    
    # init_gui handles all the GUI display when entering a mode    
    def init_gui(self):
        pass # let the subclass handle everything for the GUI - Mark [2004-10-11]

    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        pass # let the subclass handle everything for the GUI - Mark [2004-10-11]
        
# == LMB event handling methods ====================================

# Important Terms: [mark 060205]
#
# "selection curve": the collection of line segments drawn by the cursor when defining
# the selection area.  These line segments become the selection lasso when (and if) 
# the selection rectangle disappears. When the selection rectangle is still displayed,
# the selection curve consists of those line segment that are drawn between opposite 
# corners of the selection rectangle. The line segments that define/draw the 
# rectangle itself are not part of the selection curve, however.
# Also, it is worth noting that the line segments of the selection curve are also drawn 
# just beyond the front clipping plane. The variable <selCurve_List> contains the list
# of points that draw the line segments of the selection curve.
#
# "selection area": determined by the selection curve, it is the area that defines what
# is picked (or unpicked).  The variable <selArea_List> contains the list of points that
# define the selection area used to pick/unpick objects. The points in <selArea_List> 
# lay in the plane parallel to the screen and pass through the center of the view.
#
# "selection rectangle": the rectangular selection determined by the first and last points 
# of a selection curve.  These two points define the opposite corners of the rectangle.
#
# "selection lasso": the lasso selection defined by all the points (and line segements)
# in the selection curve.
            
# == LMB down-click (button press) methods
   
    def leftDown(self, event):
        self.start_selection_curve(event, START_NEW_SELECTION)

    def leftCntlDown(self, event):
        self.start_selection_curve(event, SUBTRACT_FROM_SELECTION)

    def leftShiftDown(self, event):
        self.start_selection_curve(event, ADD_TO_SELECTION)


    def start_selection_curve(self, event, sense):
        """Start a new selection rectangle/lasso.
        """
        self.selSense = sense
            # <selSense> is the type of selection, where:       
            # 0 = substract from the current selection
            # 1 = add to the current selection
            # 2 = start a new selection
        self.picking = True
            # <picking> is used to let continue_selection_curve() and end_selection_curve() know 
            # if we are in the process of defining/drawing a selection curve or not, where:
            # True = in the process of defining selection curve
            # False = finished/not defining selection curve
        #self.o.SaveMouse(event) 
            # Extracts mouse position from event and saves it in the GLPane attr "MousePos".
            #& Don't believe this is used. Mark 060205.
        #self.o.normal = self.o.lineOfSight 
            # Save the current lineOfSight vector. Use unknown.
            #& Don't believe this is used. Mark 060205.
        selCurve_pt, selCurve_AreaPt = self.o.mousepoints(event, just_beyond = 0.01)
            # mousepoints() returns a pair (tuple) of points (Numeric arrays of x,y,z)
            # that lie under the mouse pointer, just beyond the near clipping plane
            # <selCurve_pt> and in the plane of the center of view <selCurve_AreaPt>.
        self.selCurve_List = [selCurve_pt]
            # <selCurve_List> contains the list of points used to draw the selection curve.  The points lay in the 
            # plane parallel to the screen, just beyond the front clipping plane, so that they are always
            #  inside the clipping volume.
        self.o.selArea_List = [selCurve_AreaPt]
            # <selArea_List> contains the list of points that define the selection area.  The points lay in 
            # the plane parallel to the screen and pass through the center of the view.  The list
            # is used by pickrect() and pickline() to make the selection.
        self.selCurve_StartPt = self.selCurve_PrevPt = selCurve_pt
            # <selCurve_StartPt> is the first point of the selection curve.  It is used by 
            # continue_selection_curve() to compute the net distance between it and the current 
            # mouse position.
            # <selCurve_PrevPt> is the previous point of the selection curve.  It is used by 
            # continue_selection_curve() to compute the distance between the current mouse 
            # position and the previous one.
            # Both <selCurve_StartPt> and <selCurve_PrevPt> are used by 
            # basicMode.drawpick().
        self.selCurve_length = 0.0
            # <selCurve_length> is the current length (sum) of all the selection curve segments.

# == LMB drag methods

    def leftDrag(self, event):
        self.continue_selection_curve(event, START_NEW_SELECTION)
    
    def leftCntlDrag(self, event):
        self.continue_selection_curve(event, SUBTRACT_FROM_SELECTION)
    
    def leftShiftDrag(self, event):
        self.continue_selection_curve(event, ADD_TO_SELECTION)

    def continue_selection_curve(self, event, sense):
        """Add another line segment to the current selection curve.
        """
        if not self.picking: return
        
        #self.selSense = sense #& Not needed.  Confirmed by mark 060205. Remove in Phase 2.
        selCurve_pt, selCurve_AreaPt = self.o.mousepoints(event, 0.01)
            # The next point of the selection curve, where <selCurve_pt> is the point just beyond
            # the near clipping plane and <selCurve_AreaPt> is in the plane of the center of view.
        self.selCurve_List += [selCurve_pt]
        self.o.selArea_List += [selCurve_AreaPt]
        
        self.selCurve_length += vlen(selCurve_pt - self.selCurve_PrevPt)
            # add length of new line segment to <selCurve_length>.
            
        chord_length = vlen(selCurve_pt - self.selCurve_StartPt)
            # <chord_length> is the distance between the (first and last/current) endpoints of the 
            # selection curve.
        
        if self.selCurve_length < 2*chord_length:
            # Update the shape of the selection_curve.
            # The value of <selShape> can change back and forth between lasso and rectangle
            # as the user continues defining the selection curve.
            self.selShape = SELSHAPE_RECT
        else:
            self.selShape = SELSHAPE_LASSO
            
        self.selCurve_PrevPt = selCurve_pt
        
        self.o.gl_update()
        
# == LMB up-click (button release) methods

    def leftUp(self, event):
        if env.prefs[selectionBehavior_prefs_key] == A7_SELECTION_BEHAVIOR:
            self.end_selection_curve(event, ADD_TO_SELECTION) # Alpha 7 behavior (maps LMB > Shift+LMB).  Mark 051122.
        else:
            self.end_selection_curve(event, START_NEW_SELECTION)
    
    def leftCntlUp(self, event):
        self.end_selection_curve(event, SUBTRACT_FROM_SELECTION)
    
    def leftShiftUp(self, event):
        self.end_selection_curve(event, ADD_TO_SELECTION)

    def end_selection_curve(self, event, selSense):
        """Close the selection curve and do the selection.
        """
        if not self.picking: return
        self.picking = False

        selCurve_pt, selCurve_AreaPt = self.o.mousepoints(event, 0.01)

        if self.selCurve_length/self.o.scale < 0.03:
            # didn't move much, call it a click
            has_jig_selected = False
            
            if self.jigSelectionEnabled and self.jigGLSelect(event, selSense):
                has_jig_selected = True
            
            if not has_jig_selected:
                if selSense == SUBTRACT_FROM_SELECTION: 
                    self.o.assy.unpick_at_event(event)
                elif selSense == ADD_TO_SELECTION: 
                    self.o.assy.pick_at_event(event)
                elif selSense == START_NEW_SELECTION: 
                    self.o.assy.onlypick_at_event(event)
                else:
                    print 'Error in end_selection_curve(): Invalid selSense=', selSense

            # Huaicai 1/29/05: to fix zoom messing up selection bug
            # In window zoom mode, even for a big selection window, the 
            # selCurve_length/scale could still be < 0.03, so we need clean 
            # selCurve_List[] to release the rubber band selection window. One 
            # problem is its a single pick not as user expect as area pick 
        
        else:
            
            self.selCurve_List += [selCurve_pt] # Add the last point.
            self.selCurve_List += [self.selCurve_List[0]] # Close the selection curve.
            self.o.selArea_List += [selCurve_AreaPt] # Add the last point.
            self.o.selArea_List += [self.o.selArea_List[0]] # Close the selection area.
            
            self.o.shape=SelectionShape(self.o.right, self.o.up, self.o.lineOfSight)
                # Create the selection shape object.
                
            eyeball = (-self.o.quat).rot(V(0,0,6*self.o.scale)) - self.o.pov
            
            if self.selShape == SELSHAPE_RECT : # prepare a rectangle selection
                self.o.shape.pickrect(self.o.selArea_List[0], selCurve_AreaPt, -self.o.pov, selSense, \
                            eye=(not self.o.ortho) and eyeball)
            else: # prepare a lasso selection
                self.o.shape.pickline(self.o.selArea_List, -self.o.pov, selSense, \
                            eye=(not self.o.ortho) and eyeball)
        
            self.o.shape.select(self.o.assy) # do the actual selection.
                
            self.o.shape = None
                
        self.selCurve_List = []
            # (for debugging purposes, it's sometimes useful to not reset selCurve_List here,
            #  so you can see it at the same time as the selection it caused.)

        self.w.win_update()
        
# == LMB double click method

    def leftDouble(self, event):
        '''Select the part containing the atom the cursor is on.
        '''
        self.move() # go into move mode
        # bruce 040923: we use to inline the same code as is in this method
        # bruce 041217: I am guessing we still intend to leave this in,
        # here and in Move mode (to get back).
        
# == end of LMB event handlers.

    
    def setJigSelectionEnabled(self):
        self.jigSelectionEnabled = not self.jigSelectionEnabled
                 
        id = self.Menu1.idAt(3)
        self.Menu1.setItemChecked(id, self.jigSelectionEnabled)
        
                
    def Draw(self):
        # wware 060124  Embed Pyrex/OpenGL unit tests into the cad code
        if TEST_PYREX_OPENGL:
            try:
                sys.path.append("./experimental/pyrex-opengl")
                import quux
                quux.test()
                #self.w.win_update()
            except ImportError:
                env.history.message(redmsg("Can't import Pyrex OpenGL, rebuild it"))
        else:
            # bruce comment 040922: code is almost identical with modifyMode.Draw;
            # the difference (no check for self.o.assy existing) might be a bug in this version, or might have no effect.
            basicMode.Draw(self)   
            #self.griddraw()
            if self.selCurve_List: self.draw_selection_curve()
            self.o.assy.draw(self.o)

    def makeMenus(self): # menu item names modified by bruce 041217

        def fixit3(text, func):
            if self.default_mode_status_text == "Mode: " + text:
                # this menu item indicates the current mode --
                # add a checkmark and disable it [bruce 050112]
                return text, func, 'checked'
            else:
                return text, func
        
        self.Menu_spec = [
            ###e these accelerators should be changed to be Qt-official
            # by extending widgets.makemenu_helper to use Qt's setAccel...
            # [bruce 050112]
            ('Select All                     Ctrl+A', self.o.assy.selectAll),
            ('Select None                Ctrl+D', self.o.assy.selectNone),
            ('Invert Selection   Ctrl+Shift+I', self.o.assy.selectInvert),
            ('Enable Jig Selection',  self.setJigSelectionEnabled, 'checked'),
            None,
            # bruce 041217 renamed Atoms and Chunks to the full names of the
            # modes they enter, and added Move Chunks too. (It was already
            # present but in a different menu. I left it there, too, for the
            # sake of existing users. But it would be better to remove it.)
            #bruce 051213 reordered these to conform with toolbar.
            fixit3(('Select Chunks'), self.w.toolsSelectMolecules),
            fixit3(('Select Atoms'), self.w.toolsSelectAtoms),
            ('Move Chunks', self.w.toolsMoveMolecule), 
            ('Build Atoms', self.w.toolsBuildAtoms),
            ]
        
        self.Menu_spec_shift = [
            ('Delete        Del', self.o.assy.delete_sel),
            ('Move', self.move), # redundant but intentionally left in for now
            None,
            ('Hide', self.o.assy.Hide),
            None,
            ('Stretch', self.o.assy.Stretch) ]
        
        self.Menu_spec_control = [
            ('Invisible', self.w.dispInvis),
            None,
            ('Default', self.w.dispDefault),
            ('Lines', self.w.dispLines),
            ('CPK', self.w.dispCPK),
            ('Tubes', self.w.dispTubes),
            ('VdW', self.w.dispVdW),
            None,
            ('Chunk Color...', self.w.dispObjectColor),
            ('Reset Chunk Color', self.w.dispResetChunkColor),
            ('Reset Atoms Display', self.w.dispResetAtomsDisplay),
            ('Show Invisible Atoms', self.w.dispShowInvisAtoms),
            ]

    def move(self):
        # we must set OldCursor to the MoveSelectCursor before going into move mode.
        # go into move mode [bruce 040923: now also called from leftDouble]
        self.o.setMode('MODIFY') # [bruce 040923: i think how we do this doesn't need to be changed]

    pass # end of class selectMode
    
class selectMolsMode(selectMode):
        modename = 'SELECTMOLS'
        default_mode_status_text = "Mode: Select Chunks"
    
        def Enter(self): 
            basicMode.Enter(self)
            self.o.assy.pickParts() # josh 10/7 to avoid race in assy init
            
        def init_gui(self):
            selectMode.init_gui(self)
            self.o.setCursor(self.w.SelectMolsCursor)
            self.w.OldCursor = QCursor(self.o.cursor())
            self.w.toolsSelectMoleculesAction.setOn(1) # toggle on the "Select Chunks" tools icon
            self.w.selectMolDashboard.show()
            
        def restore_gui(self):
            self.w.selectMolDashboard.hide()
        
        def keyPress(self,key):
            basicMode.keyPress(self, key)
            if key == Qt.Key_Shift:
                self.o.setCursor(self.w.SelectMolsAddCursor)
            if key == Qt.Key_Control:
                self.o.setCursor(self.w.SelectMolsSubtractCursor)
                
        def keyRelease(self,key):
            basicMode.keyRelease(self, key)
            if key == Qt.Key_Shift or key == Qt.Key_Control:
                self.o.setCursor(self.w.SelectMolsCursor)
                
        def rightShiftDown(self, event):
            basicMode.rightShiftDown(self, event)
            self.o.setCursor(self.w.SelectMolsCursor)
           
        def rightCntlDown(self, event):          
            basicMode.rightCntlDown(self, event)
            self.o.setCursor(self.w.SelectMolsCursor)


class selectAtomsMode(selectMode):
        modename = 'SELECTATOMS'
        default_mode_status_text = "Mode: Select Atoms"
        
        eCCBtab1 = [1,2, 5,6,7,8,9,10, 13,14,15,16,17,18, 32,33,34,35,36, 51,52,53,54]
        
        #def __init__(self, glpane):
        #    selectMode.__init__(self, glpane)
        #    self.w.filterCheckBox.setChecked(0)
            
     
        def Enter(self): 
            basicMode.Enter(self)
            self.o.assy.selectAtoms()
            self.w.elemFilterComboBox.setCurrentItem(0) ## Disable filter by default
            # Reinitialize previously picked atoms (ppas).
            self.o.assy.ppa2 = self.o.assy.ppa3 = None
            
            
        def init_gui(self):
            selectMode.init_gui(self)
            self.o.setCursor(self.w.SelectAtomsCursor)
            self.w.toolsSelectAtomsAction.setOn(1) # toggle on the "Select Atoms" tools icon
            
            #self.w.connect(self.w.elemFilterComboBox, SIGNAL("activated(int)"), self.elemChange)
            self.w.connect(self.w.transmuteButton, SIGNAL("clicked()"), self.transmutePressed)
            
            self.update_hybridComboBox(self.w)
            self.w.selectAtomsDashboard.show()

        def restore_gui(self):
            self.w.disconnect(self.w.transmuteButton, SIGNAL("clicked()"), self.transmutePressed)
            self.w.selectAtomsDashboard.hide()
         
        
        def getDstElement(self):
            '''Return the destination element user wants to transmute to. '''
            return self.eCCBtab1[self.w.transmute2ComboBox.currentItem()] 
            
            
        def getAtomtype(self, elmNo): 
            '''<Param> elm: the current transmuted to element 'atom number'.
                return the current pastable atomtype'''
            elm = PeriodicTable.getElement(elmNo)
            atomtype = None
            if len(elm.atomtypes) > 1: 
                try: 
                    hybname = self.w.atomSelect_hybridComboBox.currentText()
                    atype = elm.find_atomtype(hybname)
                    if atype is not None:
                        atomtype = atype
                except:
                    print_compact_traceback("exception (ignored): ") # error, but continue
                pass
            if atomtype is not None and atomtype.element is elm:
                return atomtype
            
            # For element that doesn't support hybridization
            return elm.atomtypes[0]
            
    
    
        def transmutePressed(self):
            '''Slot method, called when transmute button was pressed. '''
            force = self.w.transmuteCheckBox.isChecked()
            
            dstElem = self.getDstElement()
            atomType = self.getAtomtype(dstElem)
            self.w.assy.modifyTransmute(dstElem, force = force, atomType=atomType)
            
            
        #def elemChange(self, idx):
        #    '''Slot method, called when element is changed.'''
            #if idx == 0: ## The first item: all types
            #    self.w.filterCheckBox.setChecked(False)
            #else:
            #    self.w.filterCheckBox.setChecked(True)
                
                
        def keyPress(self,key):
            from MWsemantics import eCCBtab2
            
            basicMode.keyPress(self, key)
            if key == Qt.Key_Shift:
                self.o.setCursor(self.w.SelectAtomsAddCursor)
            if key == Qt.Key_Control:
                self.o.setCursor(self.w.SelectAtomsSubtractCursor)
            # Shortcut keys for atom type in selection filter.  Bug/NFR 649. Mark 050711.
            for sym, code, num in elemKeyTab:
                if key == code:
                    line = eCCBtab2[num] + 1
                    self.w.elemFilterComboBox.setCurrentItem(line)
                    #self.elemChange(line)
                    
                              
        def keyRelease(self,key):
            basicMode.keyRelease(self, key)
            if key == Qt.Key_Shift or key == Qt.Key_Control:
                self.o.setCursor(self.w.SelectAtomsCursor)
       
       
        def rightShiftDown(self, event):
            basicMode.rightShiftDown(self, event)
            self.o.setCursor(self.w.SelectAtomsCursor)
           
        def rightCntlDown(self, event):          
            basicMode.rightCntlDown(self, event)
            self.o.setCursor(self.w.SelectAtomsCursor)
            
        def leftDouble(self, event): # mark 060128.
            '''Double click event handler for the left mouse button. 
            If an atom was double-clicked, select all the atoms reachable through 
            any sequence of bonds to that atom. Otherwise, do nothing.
            '''
            # Since we cannot determine which atom was most recently selected
            # in Select Atoms mode (unless there is a way I'm not aware of), the 
            # best we can do for now is support this when only one atom is double
            # clicked. This works well for Standard selection behavior, which is the most
            # common case. mark 060128.
            # Also, there is currently no leftShiftDouble() event handler.  When we
            # can determine which atom was most recently selected, we should
            # add this event handler. mark 060128.
            if len(self.o.assy.selatoms.values()) == 1:
                self.o.assy.selectConnected(self.o.assy.selatoms.values())
                    # The only reason this currently works is that the first click of the
                    # double click clears the selection and picks the atom under the
                    # cursor.  This does not work when holding down the Shift key.
        
        def update_hybridComboBox(self, win, text = None): 
            '''Based on the same named function in depositMode.py.
              Put the names of the current element's hybridization types into win.hybridComboBox; select the specified one if provided'''
            # I'm not preserving current setting, since when user changes C(sp2) to N, they might not want N(sp2).
            # It might be best to "intelligently modify it", or at least to preserve it when element doesn't change,
            # but even the latter is not obvious how to do in this code (right here, we don't know the prior element).
            #e Actually it'd be easy if I stored the element right here, since this is the only place I set the items --
            # provided this runs often enough (whenever anything changes the current element), which remains to be seen.
            
            elem = PeriodicTable.getElement(self.getDstElement()) 
            if text is None: 
                # Preserve current setting (by name) when possible, and when element is unchanged (not sure if that ever happens).
                # I'm not preserving it when element changes, since when user changes C(sp2) to N, they might not want N(sp2).
                # [It might be best to "intelligently modify it" (to the most similar type of the new element) in some sense,
                #  or it might not (too unpredictable); I won't try this for now.]
                text = str(win.atomSelect_hybridComboBox.currentText() )
            win.atomSelect_hybridComboBox.clear()
            atypes = elem.atomtypes
            if len(atypes) > 1:
                for atype in atypes:
                    win.atomSelect_hybridComboBox.insertItem( atype.name)
                    if atype.name == text:
                        win.atomSelect_hybridComboBox.setCurrentItem( win.atomSelect_hybridComboBox.count() - 1 ) #k sticky as more added?
                win.atomSelect_hybridComboBox.show()
            else:
                win.atomSelect_hybridComboBox.hide()
            return


        def _highlightAtoms(self, grp):
            '''High light atoms or chunks inside ESPImage jigs. '''
            from jigs_planes import ESPImage
            
            if isinstance(grp, ESPImage): 
                grp.highlightAtomChunks()
            elif isinstance(grp, Group):    
                for m in grp.members:
                    if isinstance(m, ESPImage):
                        m.highlightAtomChunks()
                    elif isinstance(m, Group):
                        self._highlightAtoms(m)
        
                        
        def Draw(self):
            '''Draw model for the select Atom mode'''
            selectMode.Draw(self)
            
            self._highlightAtoms(self.o.assy.part.topnode)
    