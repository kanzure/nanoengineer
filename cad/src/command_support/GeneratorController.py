# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
GeneratorController.py - subclass of GeneratorBaseClass, which can control
the interaction between a dialog and a plugin_generator
(supplied as constructor arguments)

@author: Bruce
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

Note: this is presently used only by features that never got fully ported
to Qt4, and which should be heavily rewritten when they do get ported
(for example, to use EditCommand instead of GeneratorBaseClass).
However, until that happens, this file should remain in the source code
so it can be maintained in trivial ways (imports, external method names).
"""

import foundation.env as env

from command_support.GeneratorBaseClass import GeneratorBaseClass

class GeneratorController(GeneratorBaseClass):
    """
    Provide the slot methods from GeneratorBaseClass to receive button clicks from a generator dialog,
    and let it run the sponsor button image in that dialog,
    but to set parameters for GeneratorBaseClass or to actually generate something,
    ask our own plugin_generator (an init argument) what to do.
       This might need to keep refs to the dialog and to its plugin_generator,
    which means it will have cyclic refs (since at least the dialog has to know who it is),
    which means it might need a destroy method (at least to break the cycles).
    """
    def __init__(self, win, dialog, plugin_generator):
        # set up attributes which GeneratorBaseClass expects to find
        gen = self.gen = plugin_generator
        self.sponsor_keyword = gen.topic
        self.prefix = "%s-" % gen.what_we_generate # GBC appends a serno and uses it for a history message;
            # if we want to use the same thing as the node name, we have to #####
        self.cmdname = "Insert %s" % gen.what_we_generate # used for Undo history
        # tell the dialog to tell us when we need to generate things, and to call our meet_dialog method
        dialog.set_controller(self)
            # (It might be better if we could do this after GeneratorBaseClass.__init__,
            #  since if this gets button presses and calls build_struct right now, it won't work;
            #  but we can't, since GBC needs self.sponsor_btn which the above method's callback to here
            #  (meet_dialog) sets from the dialog.
            #  But the caller has normally not shown the dialog yet, so hopefully that can't happen.
            #  Maybe this can be cleaned up somehow, perhaps only by modifying GeneratorBaseClass.)
        GeneratorBaseClass.__init__(self, win)
        # set some attrs our own methods need
        self.paramnames = gen.paramnames_order
        return

    def meet_dialog(self, dialog):
        """
        Start controlling this dialog's appearance and implementing its buttons.
        [This is a callback from dialog set_controller().]
        """
        self.dialog = dialog
        self.sponsor_btn = dialog.sponsor_btn # we have to set this so our superclass can see it
        ###e more
        #k not sure if we need this anymore as a separate method -- it's just a callback from set_controller
        return
    def forget_dialog(self, dialog):
        """
        Stop controlling this dialog in any way.
        """
        if self.dialog is dialog:
            self.sponsor_btn = None
            self.dialog = None
            ##e more
        else:
            print "error: self.dialog %r is not dialog %r" % (self.dialog, dialog)
        return

    def destroy(self):
        """
        To be called from the owning generator, only.
        """
        ####@@@@ but it's also called below
        if self.dialog:
            self.dialog.set_controller(None) # calls self.forget_dialog
        self.gen = None
        #e anything needed in the superclasses?
        return

    # These are defined in GeneratorBaseClass and don't need to be overridden here,
    # but they do need to be called from our dialog when its buttons are clicked on.
    # I think we'll also need to add a "restore defaults".
    ##def done_btn_clicked(self): # same as ok
    ##def preview_btn_clicked(self):
    ##def whatsthis_btn_clicked(self):
    ##def ok_btn_clicked(self):
    ##def cancel_btn_clicked(self):

    def gather_parameters(self):
        getters = self.dialog.param_getters
        res = []
        for paramname in self.paramnames:
            getter = getters[paramname] #e need error msg if missing from dialog, but exception from here still makes sense
            val = getter() #e catch this too, turn into error msg (our own kind of exception, caught by caller)
            res.append(val)
        return tuple(res)

    def build_struct(self, name, params, position):
        # name = self.name # set by the superclass (though it would make more sense if it passed it to us)
        return self.gen.build_struct(name, params, position)

    # needed by GeneratorBaseClass since we're not inheriting QDialog but delegating to one;
    # this is also the only way we can find out when the dialog gets dismissed
    # (at least I think it is, and it's also a guess that we always find out this way)
    def accept(self):
        if self.dialog:
            self.dialog.accept()
            self.dismissed()
    def reject(self):
        if self.dialog:
            self.dialog.reject()
            self.dismissed()
    def dismissed(self):
        if env.debug():
            print "debug fyi: dismissed -- should we tell owner to destroy us? is it even still there?" ####@@@@
        self.destroy() # let's just take the initiative ourselves, though it might cause bugs, maybe we should do it later...
    pass # end of class GeneratorController

# end
