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
    def __init__(self,parent = None,name = None,fl = 0):

        global windowList
        MainWindow.__init__(self,parent,name,fl)
        
        # start with empty window
        self.assy = assembly(self)
        windowList += [self]
        if name == None:
            self.setName("Atom")


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
            fn = QFileDialog.getSaveFileName(dir + fil + ".mmp",
                                             "Molecular machine parts (*.mmp)",
                                             self )
            if fn:
                fn = str(fn)
                dir, fil, ext = fileparse(fn)
                self.assy.writemmp(dir + fil + ".mmp")

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

    def editRedo(self):
        print "MWsemantics.editRedo(): Not implemented yet"

    def editCut(self):
        print "MWsemantics.editCut(): Not implemented yet"

    def editCopy(self):
        print "MWsemantics.editCopy(): Not implemented yet"

    def editPaste(self):
        print "MWsemantics.editPaste(): Not implemented yet"

    def editFind(self):
        print "MWsemantics.editFind(): Not implemented yet"

    ###################################
    # functions from the "Display" menu
    ###################################

    # this will pop up a new window onto the same assembly
    def dispNewView(self):
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
    def dispOrtho(self):
        self.glpane.ortho = 1
        self.glpane.paintGL()

    def dispPerspec(self):
        self.glpane.ortho = 0
        self.glpane.paintGL()

    # set display formats in whatever is selected,
    # or the GLPane global default if nothing is
    def dispDefault(self):
        self.setdisplay(diDEFAULT)

    def dispInvis(self):
        self.setdisplay(diINVISIBLE)

    def dispVdW(self):
        self.setdisplay(diVDW)

    def dispTubes(self):
        self.setdisplay(diTUBES)

    def dispCPK(self):
        self.setdisplay(diCPK)

    def dispLines(self):
        self.setdisplay(diLINES)

    def setdisplay(self, form):
        if self.assy and self.assy.selatoms:
            for ob in self.assy.selatoms.itervalues():
                ob.display = form
                ob.molecule.changeapp()
        elif self.assy and self.assy.selmols:
            for ob in self.assy.selmols:
                ob.display = form
                ob.changeapp()
        else:
            if self.glpane.display == form: return
            self.glpane.display = form
            for ob in self.assy.molecules:
                if ob.display == diDEFAULT:
                    ob.changeapp()
        self.assy.updateDisplays()
        

    # set the color of the selected part(s) (molecule)
    # or the background color if no part is selected.
    # atom colors cannot be changed singly
    def dispColor(self):
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

    def makeMotor(self):
        if not self.assy: return
        self.assy.makemotor(self.glpane.lineOfSight)
        self.assy.updateDisplays()

    def makeLinearMotor(self):
        if not self.assy: return
        self.assy.makeLinearMotor(self.glpane.lineOfSight)
        self.assy.updateDisplays()


    def makeBearing(self):
        print "MWsemantics.makeBearing(): Not implemented yet"

    def makeSpring(self):
        print "MWsemantics.makeSpring(): Not implemented yet"

    def makeDyno(self):
        print "MWsemantics.makeDyno(): Not implemented yet"

    def makeHeatsink(self):
        print "MWsemantics.makeHeatsink(): Not implemented yet"

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

    def helpAbout(self):
        print "MWsemantics.helpAbout(): Not implemented yet"

    ##############################################################
    # functions from the buttons down the left side of the display
    ##############################################################

    # set up cookiecutter mode
    def cookieCut(self):
        self.glpane.setMode('COOKIE')

    # "push down" one nanometer to cut out the next layer
    def cookieLayer(self):
        if self.glpane.shape:
            t = self.glpane.shape.curves[-1].thick
            self.glpane.zpush(t[1] - t[0])
            self.assy.updateDisplays()

    # fill the shape created in the cookiecutter with actual
    # carbon atoms in a diamond lattice (including bonds)
    def cookieBake(self):
        self.glpane.mode.Done()

    # the elements combobox:
    # change selected atoms to the element selected
    def elemChange(self, string):
        if self.assy.selatoms:
            for a in self.assy.selatoms.itervalues():
                a.mvElement(fullnamePeriodicTable[str(string)])
            self.assy.updateDisplays()
        else:
            self.assy.DesiredElement = fullnamePeriodicTable[str(string)].symbol

    def setCarbon(self):
        self.assy.DesiredElement = "C"
        self.comboBox1.setCurrentItem(0)

    def setHydrogen(self):
        self.assy.DesiredElement = "H"
        self.comboBox1.setCurrentItem(1)

    def setOxygen(self):
        self.assy.DesiredElement = "O"
        self.comboBox1.setCurrentItem(2)

    def setNitrogen(self):
        self.assy.DesiredElement = "N"
        self.comboBox1.setCurrentItem(3)

    def setBoron(self):
        self.assy.DesiredElement = "B"
        self.comboBox1.setCurrentItem(4)

    
    ###################################
    # some unimplemented buttons:
    ###################################

    # turn on and off an "add atom with a mouse click" mode
    def addAtomStart(self):
        self.glpane.setMode('DEPOSIT')
    
    def addAtomDone(self):
        self.glpane.mode.Done()

    # create bonds where reasonable within selection
    def movie(self):
        dir, fil, ext = fileparse(self.assy.filename)
        self.glpane.startmovie(dir + fil + ".dpb")

    # create bonds where reasonable between selected and unselected
    def bondEdge(self):
        print "MWsemantics.bondEdge(): Not implemented yet"

    # (stolen button) turn on or off the axis icon
    def ubondAll(self):
        self.glpane.drawAxisIcon = not self.glpane.drawAxisIcon
        self.glpane.paintGL()

    # break bonds between selected and unselected atoms
    def ubondEdge(self):
        print "MWsemantics.ubondEdge(): Not implemented yet"

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
    def copyBond(self):
        print "MWsemantics.copyBond(): Not implemented yet"

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

