import qt
from qt import QMainWindow, QPixmap, QWidget, QFrame, QPushButton
from qt import QGroupBox, QComboBox, QAction, QMenuBar, QPopupMenu
from qt import SIGNAL, QFileDialog
from GLPane import *
import os
import help
import icons

from constants import *
from chem import fullnamePeriodicTable

from MainWindowUI import MainWindow
helpwindow = None
windowList = []


def fileparse(name):
    """breaks name into directory, main name, and extension in a tuple.
    fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')
    """
    m=re.match("(.*\/)*([^\.]+)(\..*)?",name)
    return ((m.group(1) or "./"), m.group(2), (m.group(3) or ""))

class MWsemantics(MainWindow):
    def __init__(self,parent = None, name = None, fl = 0):
	
        ### Added by Huaicai
        #self.glpane = GLPane(self.assy)	

        global windowList
        MainWindow.__init__(self, parent, name, fl)
        
        windowList += [self]
	# start with empty window
        self.assy = assembly(self)
        if name == None:
            self.setName("Atom")

        self.Element = 'C'


        self.glpane = GLPane(self.assy, self.frame4, "glpane", self)
        
	
        self.frame4Layout.addWidget(self.glpane)


    ###################################
    # functions from the "File" menu
    ###################################

    def fileNew(self):
        """If this window is empty (has no assembly), do nothing.
        Else create a new empty one.
        """
        if self.assy:
            foo = MWsemantics()
            foo.show()

    def fileOpen(self):

        wd = globalParms['WorkingDirectory']
        fn = QFileDialog.getOpenFileName(wd, "Molecular machine parts (*.mmp);;Molecules (*.pdb);;Molecular parts assemblies (*.mpa);; All of the above (*.pdb *.mmp *.mpa)",
                                         self )
        fn = str(fn)
        if not os.path.exists(fn): return
        if not self.assy:
            dir, fil, ext = fileparse(fn)
            self.assy = assembly(self, fil)
            self.glpane.assy = self.assy
        if fn[-3:] == "pdb":
            self.assy.readpdb(fn)
        if fn[-3:] == "mmp":
            self.assy.readmmp(fn)

        self.setCaption(self.trUtf8("Atom: " + self.assy.name))

        self.glpane.scale=self.assy.bbox.scale()
        self.assy.updateDisplays()


    def fileSave(self):
        if self.assy:
            if self.assy.filename:
                fn = str(self.assy.filename)
                dir, fil, ext = fileparse(fn)
                self.assy.writemmp(dir + fil + ".mmp")
            else: self.fileSaveAs()

    def fileSaveAs(self):
        if self.assy:
            if self.assy.filename:
                dir, fil, ext = fileparse(self.assy.filename)
            else: dir, fil = "./", self.assy.name
            
	    fileDialog = QFileDialog(dir, "Molecular machine parts (*.mmp);;Molecules (*.pdb)", 								        self, "Save File As", 1)
            if self.assy.filename:
                fileDialog.setSelection(fil)

            fileDialog.setMode(QFileDialog.AnyFile)
	    if fileDialog.exec_loop() == QDialog.Accepted:
            	fn = fileDialog.selectedFile()
            if fn:
                fn = str(fn)
                dir, fil, ext = fileparse(fn)
                ext = fileDialog.selectedFilter()
                ext = str(ext)
                if ext[-4:-1] == "mmp":
                    self.assy.writemmp(dir + fil + ".mmp")
                elif ext[-4:-1] == "pdb":
                    self.assy.writepdb(dir + fil + ".pdb")

    def fileImage(self):
        if self.assy:
            if self.assy.filename:
                fn = str(self.assy.filename)
                dir, fil, ext = fileparse(fn)
            else: dir, fil, ext = "./", "Picture", "jpg"
        fn = QFileDialog.getSaveFileName(dir + fil + ".jpg",
                                         "JPEG images (*.jpg *.jpeg",
                                         self )
        fn = str(fn)
        self.glpane.image(fn)

    ###################################
    # functions from the "Edit" menu
    ###################################

    def editUndo(self):
        print "MWsemantics.editUndo(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editRedo(self):
        print "MWsemantics.editRedo(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editCut(self):
        print "MWsemantics.editCut(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editCopy(self):
        print "MWsemantics.editCopy(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editPaste(self):
        print "MWsemantics.editPaste(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editFind(self):
        print "MWsemantics.editFind(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    ###################################
    # functions from the "Display" menu
    ###################################

    # this will pop up a new window onto the same assembly
    def windowNewWindow(self):
	if self.assy:
            foo = MWsemantics()
	    foo.assy = foo.glpane.assy = self.assy
            foo.assy.windows += [foo]
	    foo.glpane.scale=self.glpane.scale
	    for mol in foo.glpane.assy.molecules:
	        mol.changeapp()
	    foo.show()
            self.assy.updateDisplays()
	

    # GLPane.ortho is checked in GLPane.paintGL
    def viewOrtho(self):
        self.glpane.ortho = 1
        self.glpane.paintGL()

    def viewPerspec(self):
        self.glpane.ortho = 0
        self.glpane.paintGL()

    # set display formats in whatever is selected,
    # or the GLPane global default if nothing is
    def dispDefault(self):
        self.setDisplay(diDEFAULT)

    def dispInvis(self):
        self.setDisplay(diINVISIBLE)

    def dispVdW(self):
        self.setDisplay(diVDW)

    def dispTubes(self):
        self.setDisplay(diTUBES)

    def dispCPK(self):
        self.setDisplay(diCPK)

    def dispLines(self):
        self.setDisplay(diLINES)

    def setDisplay(self, form):
        if self.assy and self.assy.selatoms:
            for ob in self.assy.selatoms.itervalues():
                ob.setDisplay(form)
        elif self.assy and self.assy.selmols:
            for ob in self.assy.selmols:
                ob.setDisplay(form)
        else:
            if self.glpane.display == form: return
            self.glpane.setDisplay(form)
        self.assy.updateDisplays()
        

    # set the color of the selected part(s) (molecule)
    # or the background color if no part is selected.
    # atom colors cannot be changed singly
    def dispObjectColor(self):
        c = self.colorchoose()
        if self.assy and self.assy.selmols:
            for ob in self.assy.selmols:
                ob.setcolor(c)
        else: self.glpane.backgroundColor = c
        self.assy.updateDisplays()
        

    ###################################
    # functions from the "Grid" menu
    ###################################

    # this works by setting the griddraw method of the GLPane
    # to the appropriate function

    def gridNone(self):
        self.glpane.griddraw=nogrid
        self.assy.updateDisplays()

    def gridSquare(self):
        self.glpane.griddraw=rectgrid
        self.assy.updateDisplays()

    def gridDiamond(self):
        self.glpane.griddraw=diamondgrid
        self.assy.updateDisplays()

    def gridGraphite(self):
        print "MWsemantics.gridGraphite(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    ###################################
    # functions from the "Orientation" menu
    ###################################

    # points of view corresponding to the three crystal
    # surfaces of diamond

    # along one axis
    def orient100(self):
        self.glpane.snapquat100()

    # halfway between two axes
    def orient110(self):
        self.glpane.snapquat110()

    # equidistant from three axes
    def orient111(self):
        self.glpane.snapquat111()

    # functions from the "Select" menu

    def selectAll(self):
        """Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        """
        self.assy.selectAll()

    def selectNone(self):
        self.assy.selectNone()

    def selectInvert(self):
        """If some parts are selected, select the other parts instead.
        If some atoms are selected, select all currently unselected
        atoms in parts in which there are currently some selected atoms.
        (And unselect all currently selected atoms.)
        """
        self.assy.selectInvert()

    def selectConnected(self):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        """
        self.assy.selectConnected()


    def selectDoubly(self):
        """Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds.
        """
        self.assy.selectDoubly()

    ###################################
    # Functions from the "Make" menu
    ###################################

    # these functions (do or will) create small structures that
    # describe records to send to the simulator
    # they don't do much in Atom itself
    def makeGround(self):
        if not self.assy: return
        self.assy.makeground()
        self.assy.updateDisplays()

    def makeHandle(self):
        print "MWsemantics.makeHandle(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def makeMotor(self):
        if not self.assy: return
        self.assy.makemotor(self.glpane.lineOfSight)
        self.assy.updateDisplays()

    def makeLinearMotor(self):
        if not self.assy: return
        self.assy.makeLinearMotor(self.glpane.lineOfSight)
        self.assy.updateDisplays()


    def makeBearing(self):
        QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def makeSpring(self):
        QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
    def makeDyno(self):
        print "MWsemantics.makeDyno(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def makeHeatsink(self):
        print "MWsemantics.makeHeatsink(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    ###################################
    # functions from the "Modify" menu
    ###################################

    # change surface atom types to eliminate dangling bonds
    # a kludgey hack
    def modifyPassivate(self):
        self.assy.modifyPassivate()

    # add hydrogen atoms to each dangling bond
    def modifyHydrogenate(self):
        self.assy.modifyHydrogenate()

    # form a new part (molecule) with whatever atoms are selected
    def modifySeparate(self):
        self.assy.modifySeparate()

    # Modify motor property
    def modifyMotorProperty(self):
        motorDialog = MotorPropDialog(self)
	motorDialog.exec_loop()


    ###################################
    # Functions from the "Help" menu
    ###################################

    def helpContents(self):
        global helpwindow
        if not helpwindow: helpwindow = help.Help()
        helpwindow.show()

    def helpIndex(self):
        print "MWsemantics.helpIndex(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
    def helpAbout(self):
        QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")


    ##############################################################
    # functions from the buttons down the left side of the display
    ##############################################################

    # set up cookiecutter mode
    def toolsCookieCut(self):
        self.glpane.setMode('COOKIE')

    # "push down" one nanometer to cut out the next layer
    def toolsCCAddLayer(self):
        if self.glpane.shape:
            self.glpane.pov -= self.glpane.shape.pushdown()
            self.assy.updateDisplays()

    # fill the shape created in the cookiecutter with actual
    # carbon atoms in a diamond lattice (including bonds)
    def toolsDone(self):
        self.glpane.mode.Done()

    # turn on and off an "add atom with a mouse click" mode
    def addAtomStart(self):
        self.glpane.setMode('DEPOSIT')
    
    def addAtomDone(self):
        self.glpane.mode.Done()

    # the elements combobox:
    # change selected atoms to the element selected
    def elemChange(self, string):
        if self.assy.selatoms:
            for a in self.assy.selatoms.itervalues():
                a.mvElement(fullnamePeriodicTable[str(string)])
            self.assy.updateDisplays()
        else:
            self.Element = fullnamePeriodicTable[str(string)].symbol

    def setCarbon(self):
        self.Element = "C"
        self.comboBox1.setCurrentItem(0)

    def setHydrogen(self):
        self.Element = "H"
        self.comboBox1.setCurrentItem(1)

    def setOxygen(self):
        self.Element = "O"
        self.comboBox1.setCurrentItem(2)

    def setNitrogen(self):
        self.Element = "N"
        self.comboBox1.setCurrentItem(3)

    def setBoron(self):
        self.Element = "B"
        self.comboBox1.setCurrentItem(4)


    # Play a movie from the simulator
    def toolsMovie(self):
        dir, fil, ext = fileparse(self.assy.filename)
        self.glpane.startmovie(dir + fil + ".dpb")

    
    ###################################
    # some unimplemented buttons:
    ###################################
    # create bonds where reasonable between selected and unselected
    def bondEdge(self):
        print "MWsemantics.bondEdge(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    # Turn on or off the axis icon
    def dispTrihedron(self):
        self.glpane.drawAxisIcon = not self.glpane.drawAxisIcon
        self.glpane.paintGL()

    # break bonds between selected and unselected atoms
    def modifyDeleteBond(self):
        print "MWsemantics.modifyDeleteBond(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    # Make a copy of the selected part (molecule)
    # cannot copy individual atoms
    def copyDo(self):
        if not self.assy: return
        self.assy.copy()
        self.assy.updateDisplays()

    # 2BDone: make a copy of the selected part, move it, and bondEdge it,
    # having unselected the original and selected the copy.
    # the motion is to be the same relative motion done to a part
    # between copying and bondEdging it.
    def modifyCopyBond(self):
        print "MWsemantics.modifyCopyBond(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    # delete selected parts or atoms
    def killDo(self):
        if not self.assy: return
        self.assy.kill()
        self.assy.updateDisplays()

    # utility functions

    def colorchoose(self):
        c = QColorDialog.getColor(QColor(100,100,100), self, "choose")
        return c.red()/256.0, c.green()/256.0, c.blue()/256.0


    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete:
            self.killDo()



    ##############################################################
    # Some future slot functions for the UI                      #
    ##############################################################

    def dispBGColor(self):
        """ Change backgound color of the graphics window """
        QMessengeBox.warning(self, "ATOM User Notice:", 
		"This function is not implemented yet, coming soon...")
    def dispCsys(self):
	""" Toggle on/off center coordinate axes """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def dispDatumLines(self):
        """ Toggle on/off datum lines """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def dispDatumPlanes(self):
        """ Toggle on/off datum planes """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def dispOpenBonds(self):
        """ Toggle on/off open bonds """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editPrefs(self):
        """ Edit square grid line distances(dx, dy, dz) in nm/angtroms """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
 
    def elemChangePTable(self):
        """ Future: element change via periodic table (only elements we support) """

    def fileClear(self):
        """ Closes part without Save (Clears the graphics window) """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def fileClose(self):
	""" Closes part with Save (leaves the graphics window empty) """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def fileSetWorkDir(self):
	""" Sets working directory (need dialogue window) """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def modifyMinimize(self):
        """ Minimize """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def toolsSimulator(self):
	""" Open simulator dialog window """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def viewFitToWindow(self):
        """ Fit to Window """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
