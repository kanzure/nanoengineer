# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
THIS FILE IS PRESENTLY OWNED BY BRUCE -- please don't change it in any way,
however small, unless this is necessary to make Atom work properly for other developers.
[bruce 040921]

$Id$

Stub file for Extrude mode. For now, this works, but it's almost identical to cookieMode,
except for a different background color.
-- bruce 040924
"""

# bruce 040920: until MainWindow.ui does the following, I'll do it manually:
# (FYI: I will remove this, and the call to this, after MainWindowUI does the same stuff.
#  But first I will be editing this function a lot to get the dashboard contents that I need.)
def do_what_MainWindowUI_should_do(self):
        "self should be the main MWSemantics object -- at the moment this is a function, not a method"

        from qt import SIGNAL, QToolBar, QLabel, QLineEdit, QSpinBox

        # 1. connect the mode-entering button to its MWSemantics method 
        ## bugfix: no longer needed as of 040928 when Mark evidently added this to the .ui file! Removed by bruce 040929.
        ## self.connect(self.toolsExtrudeAction,SIGNAL("activated()"),self.toolsExtrude)
            # fyi, this is modelled after: 
            # self.connect(self.toolsCookieCutAction,SIGNAL("activated()"),self.toolsCookieCut)

        # 2. make a toolbar to be our dashboard, similar to the cookieCutterToolbar
        # (based on the code for cookieCutterToolbar in MainWindowUI)

        self.extrudeToolbar = QToolBar(QString(""),self,Qt.DockBottom)

        self.extrudeToolbar.setGeometry(QRect(0,0,515,29)) ### will probably be wrong once we modify the contents
        self.extrudeToolbar.setBackgroundOrigin(QToolBar.WidgetOrigin)

        self.textLabel_extrude_toolbar = QLabel(self.extrudeToolbar,"textLabel_extrude_toolbar") # text set below

        # these are the wrong actions to add... should cause no harm for now, tho
        self.extrudeToolbar.addSeparator()
        self.ccGraphiteAction.addTo(self.extrudeToolbar)
        self.extrudeToolbar.addSeparator()
        self.orient100Action.addTo(self.extrudeToolbar)
        self.orient110Action.addTo(self.extrudeToolbar)
        self.orient111Action.addTo(self.extrudeToolbar)
        self.extrudeToolbar.addSeparator()
        self.ccAddLayerAction.addTo(self.extrudeToolbar)
        self.extrudeToolbar.addSeparator()

        # ideally these should be known only to the mode, not be members of the main window object... and what we need is different... ok for now
        self.extrudeLineEdit = QLineEdit(self.extrudeToolbar,"extrudeLineEdit")
        self.extrudeSpinBox = QSpinBox(self.extrudeToolbar,"extrudeSpinBox")
        self.extrudeSpinBox.setValue(3) # different than in cookieMode
        
        self.extrudeToolbar.addSeparator()

        # dashboard tools shared with other modes
        self.toolsBackUpAction.addTo(self.extrudeToolbar)
        self.toolsStartOverAction.addTo(self.extrudeToolbar)
        self.toolsDoneAction.addTo(self.extrudeToolbar)
        self.toolsCancelAction.addTo(self.extrudeToolbar)

        # note: python name-mangling would turn __tr, within class MainWindow, into _MainWindow__tr (I think... seems to be right)
        self.extrudeToolbar.setLabel(self._MainWindow__tr("Extrude Mode"))
        self.textLabel_extrude_toolbar.setText(self._MainWindow__tr("Extrude Mode (stub)")) ###

        # fyi: caller hides the toolbar, we don't need to
        
        return

# ==

from modes import *

class extrudeMode(basicMode):

    # class constants
    backgroundColor = 200/256.0, 100/256.0, 100/256.0 # different than in cookieMode
    modename = 'EXTRUDE'
    default_mode_status_text = "Mode: Extrude"

    # default initial values
    ###

    # no __init__ method needed
    
    # methods related to entering this mode

##    def refuseEnter(self, warn):
##        "if we'd refuse to enter this mode, then (iff warn) tell user why, and (always) return true."
##        from debug import print_compact_stack # re-import each time, so reload(debug) is effective at runtime
##        print_compact_stack("refuseEnter")
##        assy = self.o.assy
##        if len(assy.selmols) != 1:
##            if warn:
##                self.warning("extrude mode stub requires exactly 1 molecule to be selected, for now (sorry)")
##            return 1
##        return 0
        
    def Enter(self): # bruce 040922 split setMode into Enter and show_toolbars (fyi)
        basicMode.Enter(self)
        ###
        # find out what's selected, which if ok will be the repeating unit we will extrude... explore its atoms, bonds, externs...
        # what's selected should be its own molecule if it isn't already...
        # for now let's hope it is exactly one (was checked in refuseEnter, but not anymore).
        assy = self.o.assy
        self.assy = assy ##k i hope this never changes during one use of this mode! probably this mode controls it then, right?

        ok, mol = assy_extrude_unit(self.assy)
        if not ok:
            whynot = mol
            #e show the reason why not?
            print "why not: %r" % (whynot,) ###e improve
            return 1 # refused!
        ##mol = assy.selmols[0]
        self.basemol = mol
        offset = V(15.0,16.0,17.0) #e this will be editable (what are the offset units btw?)
        self.offset = offset
        
        self.ncopies = 1 # might not be true if we reenter the mode with one copy selected! ignore that issue for now.
        ### note, nothing makes sure the new mol is visible in the window except keeping this small!!
        # now see if we can copy it, moved over a bit, and add that to the assembly

        self.molcopies = [self.basemol] # if we have any potential mols to show dimly, they are not in here

        self.update_ncopies() ##### also call when spinbox changes -- void QSpinBox::valueChanged ( int value ) [signal]

        ## from some other code:
        ## self.connect(self.NumFramesWidget,SIGNAL("valueChanged(int)"),self.NumFramesValueChanged)
        ## but we should destroy conn when we exit the mode... but i guess i can save that for later... since spinbox won't be shown then
        # and since redundant conns will not kill me for now.
        # self.w is a guess for where to put the conn, not sure it matters as long as its a Qt object
        self.w.connect(self.w.extrudeSpinBox,SIGNAL("valueChanged(int)"),self.spinbox_value_changed) #####k

        
        ###e we might optimize by not creating these, only displaying them, but i ignore this issue for now
        
##        print "adding a copy of your selected molecule"
##        mols = [mol]
##        newmols = assy_copy(assy, mols, offset = offset)
##        newmol = newmols[0]
        
        ## wrong i guess: assy.addmol(newmol)
        ###### do we need to tell it to repaint???? don't know yet
        ##### need to add some selection behavior
        ### and make the spinbox set the number of copies
        ### and change the scaleas needed for that. or show the copies that are not visible somehow, like an arrow pointing to them...
        import __main__
        __main__.mode = self
        print "fyi: __main__.mode = this extrude mode obj; use debug window"
        #### .assy

    def asserts(self):
        assert len(self.molcopies) == self.ncopies
        assert self.molcopies[0] == self.basemol

    def spinbox_value_changed(self, val):
        self.update_ncopies() # use now-current value, not the one passed (hoping something collapsed multiple sigs into one event...
        #e probably that won't happen unless we do something here to generate an event.... probably doesn't matter anyway,
        #e unless code to adjust to one more or less copy is way to slow.

    def update_ncopies(self, nwanted = None):
        """make the number and position of the copies of basemol what they should be
          (or nwanted, if supplied -- dangerous feature since not saved!! so change this so this func knows where to get that value);
           should call this in Enter and whenever relevant controls might change
        """
        self.asserts()

        if nwanted == None:
            nwanted = self.w.extrudeSpinBox.value()
        ncopies_wanted = nwanted
        ncopies_wanted = min(20,ncopies_wanted) # low upper limit, for safety, for now ###
        ncopies_wanted = max(1,ncopies_wanted) # always at least one copy ###e fix spinbox's value too?? also think about it on exit...
        if ncopies_wanted != nwanted:
            print "fyi, ncopies_wanted is limited to safe value %r, not your requested value %r" % (ncopies_wanted, nwanted)

        offset_wanted = V(15.0,16.0,17.0) #e this will be editable (what are the offset units btw?)

        # update:
        # first move the copies in common, if offset changed (which is pretty unlikely while it's hardcoded to a constant :-)
        ncopies_common = min(ncopies_wanted,self.ncopies)
        ## ncopies_new = ncopies_wanted - ncopies_common # might not need this count
        ## ncopies_obs = self.ncopies - ncopies_common # ditto
        if offset_wanted != self.offset:
            for ii in range(ncopies_common):
                if ii: self.molcopies[ii].move((offset_wanted - self.offset)*ii) #####k
            self.offset = offset_wanted
        # now delete or make copies as needed (but don't adjust view until the end)
        while self.ncopies > ncopies_wanted:
            # delete a copy we no longer want
            ii = self.ncopies - 1
            self.ncopies = ii
            old = self.molcopies.pop(ii) ######k
            self.assy.killmol(old) #####k
            self.w.modelTreeView.deleteObject(old) #k
            self.asserts()
        while self.ncopies < ncopies_wanted:
            # make a new copy we now want
            #e the fact that it shows up immediately in model tree would permit user to change its color, etc;
            #e but we'll probably want to figure out a decent name for it, make a special group to put these in, etc
            ii = self.ncopies
            self.ncopies = ii + 1
            newmols = assy_copy(self.assy, [self.basemol], offset = self.offset * ii) # includes addObject
            new = newmols[0]
            self.molcopies.append(new)
            self.asserts()
        ####
        pass
        # now we'd adjust view, or make drawing show if stuff is out of view; make atom overlaps transparent or red; etc...
        self.o.paintGL()
        return
        
    def show_toolbars(self):
        self.w.extrudeToolbar.show()

    # methods related to exiting this mode [bruce 040922 made these from old Done and Flush methods]

##    def haveNontrivialState(self): ### wrong
##        ###
##        return self.o.shape != None # note that this is stored in the glpane, but not in its assembly.
##
##    def StateDone(self): ### wrong
##        if self.o.shape:
##            self.o.assy.molmake(self.o.shape)
##        self.o.shape = None
##        return None
##
##    def StateCancel(self): ### wrong
##        self.o.shape = None
##        # it's mostly a matter of taste whether to put this statement into StateCancel, restore_patches, or clear()...
##        # it probably doesn't matter in effect, in this case. To be safe (e.g. in case of Abandon), I put it in more than one place.
##        return None
    
    def hide_toolbars(self):
        self.w.extrudeToolbar.hide()

##    def restore_patches(self): ### wrong
##        self.o.shape = None
        
    # other dashboard methods (not yet revised by bruce 040922 ###e)
    
##    def Backup(self): ### wrong
##        if self.o.shape:
##            self.o.shape.undo()
##        self.o.paintGL()

    # mouse events ### wrong -- i should let you drag one of the repeated units; see code in move mode which does similar
    
    def leftDown(self, event):
        pass##self.StartDraw(event, 1)
    
    def leftShiftDown(self, event):
        pass##self.StartDraw(event, 0)

    def leftCntlDown(self, event):
        pass##self.StartDraw(event, 2)

    def leftDrag(self, event):
        pass##self.ContinDraw(event)
    
    def leftShiftDrag(self, event):
        pass##self.ContinDraw(event)
    
    def leftCntlDrag(self, event):
        pass##self.ContinDraw(event)
    
    def leftUp(self, event):
        pass##self.EndDraw(event)
    
    def leftShiftUp(self, event):
        pass##self.EndDraw(event)
    
    def leftCntlUp(self, event):
        pass##self.EndDraw(event)


    def Draw(self):
        basicMode.Draw(self) # axes, if displayed
        ##self.griddraw()
        ##if self.sellist: self.pickdraw()
        ##if self.o.shape: self.o.shape.draw(self.o)
        self.o.assy.draw(self.o) ##### copied from selectMode.draw(). But the code inside this looks pretty weird!!!
   
    def makeMenus(self): ### not yet reviewed for extrude mode
        self.Menu1 = self.makemenu([('Cancel', self.Cancel),
                                    ('Start Over', self.StartOver),
                                    ('Backup', self.Backup),
                                    None,
                                    ('Move', self.move),
                                    ('Copy', self.copy)])
        
        self.Menu2 = self.makemenu([('Kill', self.o.assy.kill),
                                    ('Copy', self.o.assy.copy),
                                    ('Separate', self.o.assy.modifySeparate),
                                    ('Bond', self.o.assy.Bond),
                                    ('Unbond', self.o.assy.Unbond),
                                    ('Stretch', self.o.assy.Stretch)])
        
        self.Menu3 = self.makemenu([('Default', self.w.dispDefault),
                                    ('Lines', self.w.dispLines),
                                    ('CPK', self.w.dispCPK),
                                    ('Tubes', self.w.dispTubes),
                                    ('VdW', self.w.dispVdW),
                                    None,
                                    ('Invisible', self.w.dispInvis),
                                    None,
                                    ('Color', self.w.dispObjectColor)])

    def copy(self):
        print 'NYI'

    def move(self):
        print 'NYI'

    pass # end of class extrudeMode

# ==
# should be a method in assembly:
def assy_copy(assy, mols, offset = V(10.0, 10.0, 10.0)):
    """in assy, copy the mols in the list of mols; return list of new mols.
    The code is modified from assembly.copy [is that code used? correct? it doesn't do anything with nulist].
    """
    self = assy
    if mols:
        self.modified = 1
        nulist=[]
        for mol in mols[:]: # copy the list in case it happens to be self.selmols (needed??)
            numol=mol.copy(offset)
            nulist += [numol]
            self.molecules += [numol]
            self.w.modelTreeView.addObject(numol)
    return nulist

def assy_merge_mols(assy, mollist):
    "merge multiple mols in assy into one mol in assy, and return it"
    assert len(mollist) == 1, "can't yet handle general merge"
    return mollist[0]

def assy_extrude_unit(assy):
    """if we can find a good extrude unit in assy,
       make it a molecule in there, and return (True, mol);
       else return (False, whynot).
       Note: we might modify assy even if we return False in the end!!!
       #e Fix that later.
       Best solution: make a nondet version that just returns the flag, for use in refuseEnter. Should be easy enough.
    """
    if assy.selmols:
        assert type(assy.selmols) == type([]) # assumed by this code; always true at the moment
        ###e should merge the selected mols into one? or a group? or use them all each time? for now, require exactly one.
        if len(assy.selmols) > 1:
            return False, "more than one molecule selected (and stub code can't yet merge them)"
        else:
            return True, assy.selmols[0] #e later use assy_merge_mols
    elif assy.selatoms:
        res = []
        def new_old(new, old):
            assert new.atoms
            res.append(new) #e someday we might use old too, eg for undo or for heuristics to help deal with neighbor-atoms...
        assy.modifySeparate(new_old_callback = new_old) # make the selected atoms into their own mols
        assert res, "what happened to all those selected atoms???"
        if len(res) > 1:
            return False, "more than one mol contains selected atoms, and stub code can't yet merge them"
        else:
            return True, res[0] #e later use assy_merge_mols
        #e or for multiple mols, should we do several extrudes in parallel? hmm, might be useful...
    elif len(assy.molecules) == 1:
        # nothing selected, but exactly one molecule in all -- just use it
        return True, assy.molecules[0]
    else:
        return False, "nothing selected, and not exactly one mol in all, stub code gives up" #e someday might merge multiple mols...
    pass

