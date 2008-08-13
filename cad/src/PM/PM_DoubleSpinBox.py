# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_DoubleSpinBox.py

@author: Mark
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrDoubleSpinBox out of PropMgrBaseClass.py into this file
and renamed it PM_DoubleSpinBox.
"""

from PyQt4.Qt import QDoubleSpinBox
from PyQt4.Qt import QLabel
from PyQt4.Qt import QWidget

from widgets.prefs_widgets import widget_connectWithState
from widgets.prefs_widgets import QDoubleSpinBox_ConnectionWithState
from widgets.prefs_widgets import set_metainfo_from_stateref

class PM_DoubleSpinBox( QDoubleSpinBox ):
    """
    The PM_DoubleSpinBox widget provides a QDoubleSpinBox (with an 
    optional label) for a Property Manager group box.
    
    Detailed Description
    ====================
    The PM_DoubleSpinBox class provides a spin box widget (with an
    optional label) for a 
    U{B{Property Manager dialog}<http://www.nanoengineer-1.net/mediawiki/
    index.php?title=Property_Manager>} 
    that takes floats.

    PM_DoubleSpinBox allows the user to choose a value by clicking the up and 
    down buttons or by pressing Up or Down on the keyboard to increase or 
    decrease the value currently displayed. The user can also type the value 
    in manually. The spin box supports float values but can be extended to 
    use different strings with validate(), textFromValue() and valueFromText().
    
    Every time the value changes PM_DoubleSpinBox emits the valueChanged() 
    signal.The current value can be fetched with value() and set with setValue()
    
    Note: PM_DoubleSpinBox will round numbers so they can be displayed with the 
    current precision. In a PM_DoubleSpinBox with decimals set to 2, calling 
    setValue(2.555) will cause value() to return 2.56.
    
    Clicking the up and down buttons or using the keyboard accelerator's 
    Up and Down arrows will increase or decrease the current value in steps 
    of size singleStep(). If you want to change this behavior you can 
    reimplement the virtual function stepBy(). The minimum and maximum 
    value and the step size can be set using one of the constructors, 
    and can be changed later with setMinimum(), setMaximum() and 
    setSingleStep(). The spin box has a default precision of 2 decimal 
    places but this can be changed using setDecimals().
    
    Most spin boxes are directional, but PM_DoubleSpinBox can also operate 
    as a circular spin box, i.e. if the range is 0.0-99.9 and the current 
    value is 99.9, clicking "up" will give 0 if wrapping() is set to true. 
    Use setWrapping() if you want circular behavior.
    
    The displayed value can be prepended and appended with arbitrary strings 
    indicating, for example, currency or the unit of measurement. 
    See setPrefix() and setSuffix(). The text in the spin box is retrieved 
    with text() (which includes any prefix() and suffix()), or with 
    cleanText() (which has no prefix(), no suffix() and no leading or 
    trailing whitespace).
    
    It is often desirable to give the user a special (often default) choice
    in addition to the range of numeric values. See setSpecialValueText() 
    for how to do this with PM_DoubleSpinBox.
    
    @see: U{B{QDoubleSpinBox}<http://doc.trolltech.com/4/qdoublespinbox.html>}
        
    @cvar defaultValue: The default value of the spin box.
    @type defaultValue: float
    
    @cvar setAsDefault: Determines whether to reset the value of the
                        spin box to I{defaultValue} when the user clicks
                        the "Restore Defaults" button.
    @type setAsDefault: bool
    
    @cvar labelWidget: The Qt label widget of this spin box.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    """
    
    defaultValue = 0.0
    setAsDefault = True
    labelWidget  = None
    
    def __init__(self, 
                 parentWidget, 
                 label        = '', 
                 labelColumn  = 0,
                 value        = 0.0, 
                 setAsDefault = True,
                 minimum      = 0.0, 
                 maximum      = 99.0,
                 singleStep   = 1.0, 
                 decimals     = 1, 
                 suffix       = '',
                 spanWidth    = False
                 ):
        """
        Appends a QDoubleSpinBox (Qt) widget to the bottom of I{parentWidget}, 
        a Property Manager group box.
        
        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: The label that appears to the left or right of the 
                      spin box. If label contains the relative path to an 
                      icon (.png) file, that icon image will be used for the
                      label.
                      
                      If spanWidth is True, the label will be displayed on
                      its own row directly above the spin box.
                      
                      To suppress the label, set I{label} to an empty string.
        @type  label: str
        
        @param labelColumn: The column number of the label in the group box
                            grid layout. The only valid values are 0 (left 
                            column) and 1 (right column). The default is 0 
                            (left column).
        @type  labelColumn: int
        
        @param value: The initial value of the spin box.
        @type  value: float
        
        @param setAsDefault: If True, will restore I{value} when the 
                             "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        
        @param minimum: The minimum value of the spin box.
        @type  minimum: float
        
        @param maximum: The maximum value of the spin box.
        @type  maximum: float
        
        @param singleStep: When the user uses the arrows to change the 
                           spin box's value the value will be 
                           incremented/decremented by the amount of the 
                           singleStep. The default value is 1.0. 
                           Setting a singleStep value of less than 0 does 
                           nothing.
        @type  singleStep: float
        
        @param decimals: The precision of the spin box.
        @type  decimals: int
        
        @param suffix: The suffix is appended to the end of the displayed value. 
                       Typical use is to display a unit of measurement. 
                       The default is no suffix. The suffix is not displayed
                       for the minimum value if specialValueText() is set.
        @type  suffix: str
        
        @param spanWidth: If True, the spin box and its label will span the
                          width of the group box. The label will appear directly
                          above the spin box and is left justified. 
        @type  spanWidth: bool
        
        @see: U{B{QDoubleSpinBox}<http://doc.trolltech.com/4/qdoublespinbox.html>}
        @see: B{InsertNanotube_PropertyManager._chiralityFixup()} for an example
              use of blockSignals flag
        """
        
        if 0: # Debugging code
            print "PropMgrSpinBox.__init__():"
            print "  label        = ", label
            print "  labelColumn  = ", labelColumn
            print "  value        = ", value
            print "  setAsDefault = ", setAsDefault
            print "  minimum      = ", minimum
            print "  maximum      = ", maximum
            print "  singleStep   = ", singleStep
            print "  decimals     = ", decimals
            print "  suffix       = ", suffix
            print "  spanWidth    = ", spanWidth
        
        if not parentWidget:
            return
        
        QDoubleSpinBox.__init__(self)
        
        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth
        
        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)
                        
        # Set QDoubleSpinBox minimum, maximum, singleStep, decimals, then value
        self.setRange(minimum, maximum)
        self.setSingleStep(singleStep)
        self.setDecimals(decimals)
        
        self.setValue(value) # This must come after setDecimals().
        
        if setAsDefault:
            self.setDefaultValue(value)
        
        # Add suffix if supplied.
        if suffix:
            self.setSuffix(suffix)
        
        parentWidget.addPmWidget(self)
                    
    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setValue(self.defaultValue)
    
    def setDefaultValue(self, value):
        """
        Sets the default value of the spin box to I{value}. The current spin box
        value is unchanged.
                      
        @param value: The new default value of the spin box.
        @type  value: float
        
        @see: L{setValue}
        """
        self.setAsDefault = True
        self.defaultValue = value
            
    def setValue(self, 
                 value, 
                 setAsDefault = True, 
                 blockSignals = False):
        """
        Sets the value of the spin box to I{value}. 
        
        setValue() will emit valueChanged() if the new value is different from
        the old one. 
        
        @param value: The new spin box value.
        @type  value: float
        
##        @param setAsDefault: Determines if the spin box value is reset when 
##                             the "Restore Defaults" button is clicked. If True,
##                             (the default) I{value} will be used as the reset 
##                             value.
##        @type  setAsDefault: bool
        
        @note: The value will be rounded so it can be displayed with the current
        setting of decimals.  
        
        @param blockSignals: Many times, the caller just wants to setValue 
                             and don't want to send valueChanged signal. 
                             If this flag is set to True, the valueChanged 
                             signal won't be emitted.  The default value is 
                             False.
        @type  blockSignals: bool 
        
        @see: L{setDefaultValue}
        @see: QObject.blockSignals(bool block)
        
        """
        
##        if setAsDefault: ### THIS IS A BUG, if the default value of this option remains True.
##            # it also looks useless, so i'll zap it. btw that means i could zap the entire method, but i won't yet.
##            # I verified nothing calls it with changed version... not enough to prove this zapping is ok...
##            # same issue in PM_SpinBox and PropMgrBaseClass. I've discussed this with Mark & Ninad and they agree
##            # it should be changed. Ninad, feel free to clean up this method & comment when you see this.
##            # [bruce 070814]
##            self.setDefaultValue(value)
        
        
        #If blockSignals flag is True, the valueChanged signal won't be emitted 
        #This is done by self.blockSignals method below.  -- Ninad 2008-08-13
        self.blockSignals(blockSignals)
        
        QDoubleSpinBox.setValue(self, value)
        
        #Make sure to always 'unblock' signals that might have been temporarily
        #blocked before calling superclass.setValue. 
        self.blockSignals(False)

    def connectWithState(self, stateref,
                         set_metainfo = True,
                         debug_metainfo = False):
        """
        Connect self to the state referred to by stateref,
        so changes to self's value change that state's value
        and vice versa. By default, also set self's metainfo
        to correspond to what the stateref provides.

        @param stateref: a reference to state of type double,
                         which meets the state-reference interface StateRef_API.
        @type stateref: StateRef_API

        @param set_metainfo: whether to also set defaultValue, minimum,
        and/or maximum, if these are provided by the stateref. (This
        list of metainfo attributes will probably be extended.)
        
        @type set_metainfo: bool

        @param debug_metainfo: whether to print debug messages
        about the actions taken by set_metainfo, when it's true.
        
        @type debug_metainfo: bool
        """
        if set_metainfo:
            # Do this first, so old min/max don't prevent setting the
            # correct current value when we connect new state.
            #
            # REVIEW: the conventions for expressing a lack of
            # minimum, maximum, or defaultValue, either on self
            # or on the stateref, may need revision, so it's not
            # ambiguous whether the stateref knows the minimum (etc)
            # should be unset on self or doesn't care what it's set to.
            # Ideally, some explicit value of stateref.minimum
            # would correspond to "no minimum" (i.e. a minimum of
            # negative infinity), etc.
            # [bruce 070926]
            set_metainfo_from_stateref( self.setMinimum, stateref, 'minimum',
                                        debug_metainfo)
            set_metainfo_from_stateref( self.setMaximum, stateref, 'maximum',
                                        debug_metainfo)
            set_metainfo_from_stateref( self.setDefaultValue, 
                                        stateref, 
                                        'defaultValue',
                                        debug_metainfo)
        widget_connectWithState( self, stateref,
                                 QDoubleSpinBox_ConnectionWithState)
        return
        
    def hide( self ):
        """
        Hides the spin box and its label (if it has one).
        Call L{show()} to unhide the spin box.
        
        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget: 
            self.labelWidget.hide()
            
    def show( self ):
        """
        Unhides the spin box and its label (if it has one). 
        
        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget: 
            self.labelWidget.show()
        
    # End of PM_DoubleSpinBox ########################################
