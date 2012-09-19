"""
Prerequisite_ReferencePlaneIsSelected.py (scratch file)

a prerequisite for a command, which requires that a reference plane is selected.

$Id$


what is required?

a ref plane or equiv is selected

write some code to look at selection and determine that

given the model or model-with-selection

(an assy object?)

(or just a "model", implicit that it includes selection?)

(why not receive them both? and you could just pass the current part...)


anyway... it follows that flow chart i wrote, looking at params and prior-loop state
to decide what to do and what to say.


it runs through some code to compute this, may have model side effects...

when does it run? when we "enter the mode", as part of updating the UI.
we can't update the UI until it runs.
it might decide to change modes! this might repeat until it settles down!


"""

## split the code below out of this class: from Commands.Prerequisite import Prerequisite

from utilities import accumulate # combines sublists into a big one... ###IMPLEM

class PreCommand(Command):
    """
    Abstract class for a kind of temporary Command which comes before
    other commands.
    (Note: Instances of specific subclasses are single runs,
    as for all Commands.)
       Subclasses typically need to override enterSelfWithContinuations
    in a nontrivial way, and also delegate some of the command API
    to the yes_cmd continuation... eg let it describe the PM (but tell it whether the preq is satisfied)
    (but modify the PM it makes or describes, to get our own) (or, pass it values to include in the one it makes? more realistic?)

    conclusion: for now, the preq just tells the main cmd what it wants to know to make its PM
    and the main cmd has to remember to include that data in its PM desc!!

    digr: review: when a preq becomes satsified by user action responding to msg,
    do we print something into statusbar or maybe history? or when it is *not* satisfied, ditto?
    if so, do it by calling a special log-like function... at what point do we know this happened?

    ### REVIEW -- do we know yes_cmd/no_cmd at this level
    or is that constructed? typically the yes_cmd comes from the "stuff after this pre-command"
    and the no_cmd is an error handling command... which might depend -- on what?? ###
    """
    pass

class Prerequisite( PreCommand):
    # initial values of instance variables
    prerequisite_msg = None # None, or a message prefix for the PM
    # methods which subclasses should override
    def prerequisite_check(self):
        """
        (part of the Prerequisite subclass API)
        Check whether the prerequisite is satisfied in self's situation (model, selection, prefs and settings).
        Do things involving the command sequencer, messages, etc, if it is or is not... ###
        Return True (after side effects on self) if it's satisfied, false if not.
        """
        assert 0, "subclass must override this method"
    # methods which should not normally be overridden
    def enterSelfWithContinuations(self, yes_cmd, no_cmd): ### SCRATCH name and API
        """
        (proposed new part of the Command API ### REVIEW/TODO)
        Enter self, with yes_cmd being the command to run if self *eventually* succeeds
        (after whatever user interaction we can provide to help that happen),
        and no_cmd being the command to run if we give up on succeeding.
        Note: those cmds might be command instances, or just descriptions. ###TODO/REVIEW
        """
        # while self has things to do, do them (influenced by yes_cmd),
        # then decide which one to replace ourselves with (return value says that)
        # To stay in self: return True, None
        # To forward to another command immediately: return False, cmd (description or instance)
        return True, None ### STUB
    pass

class Prerequisite_ReferencePlaneIsSelected( Prerequisite):
    # initial values of instance variables
    offer_ref_planes_for_selection = False
        # whether our UI (in PM and/or graphics area) needs to offer
        # the available ref planes for selection
        ### REVIEW: do we loop around and reset this? (in which case, best to set it at start of prerequisite_check ###TODO)
        # or do we make a new preq instance in which it's already reset?? ###

    def prerequisite_check(self):
        """
        (part of the Prerequisite subclass API)
        Check whether exactly one reference plane (or equivalent) is selected.
        It's ok if other stuff is also selected.
        """
        # require that among the selected things there is exactly one reference plane or equivalent
        # (TODO: but if the same or an identical one shows up twice, ignore that!)
        # (TODO: if there is one explicit plane and other plane-equivalents,
        #  let the explicit plane trump the others)
        planes = accumulate( lambda node: node.getReferencePlanes(), self.getTopmostSelectedNodes() ) ### IMPLEM in Node & Command
        # TODO: canonicalize them and remove duplicates
        if len(planes) == 1:
            # good!
            plane = planes[0]
            self.setReferencePlane(plane) ### IMPLEM - puts it into appropriate slot in PM... how is that specified BTW?
                ### REVIEW -- is there a PM_ReferencePlaneSelector for the widget or combo which is used to help select a ref plane?
                # if so, we'd require the PM to contain one (or to be a description to which we can add one)
                ### SEE mark's user story to see what it says about this
            return True # success
        elif len(planes) == 0:
            self.prerequisite_msg = "Select a reference plane." # TODO: also say "or a surface..."
            self.offer_ref_planes_for_selection = True
            return False # failure (of our prerequisite to be met)
        elif len(planes) > 1:
            self.prerequisite_msg = "Select a single reference plane." # TODO: also say "or surface..."
            self.offer_ref_planes_for_selection = True
            # REVIEW: do we modify the UI in this case to make the already selected ones especially easy to choose from?
            return False
        pass

    # override some graphics area methods to help implement what we do ... also some actions for PM slots in the ref plane selector(?)

    def leftDown(self, event):
        ### do we let user click on a ref plane in graphics area (in 3d area or in MT-in-glpane) to select it?
        pass ###STUB

    def Draw(self, whatever):###k
        self.yes_cmd.Draw(whatever) ### TODO: I guess we need to instantiate that no matter what (be optimistic!)
            # REVIEW: maybe put it inside a wrapper to protect us from exceptions in it?
        ### now also draw the ref plane stuff -- 3d or MTi-in-glpane, for std planes or ones in model, esp selected ones
        return

    # also whatever we need to handle the PM widget for this
    # REVIEW: the PM widget goes with this preq object... but what delegates to what? it seems like this preq is in control...
    # as if we took the cmd Seq( preq, yes_cmd) and rewrote it to something fancier, sort of preq(yes_cmd, std_error_handler)


