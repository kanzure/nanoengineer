
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
$Id$


old code for ToggleShow [nim], taken from testdraw2_cannib.py

# types
##ImageWidget = Widget # not sure if we want this to be a definite subtype
# could it be renamed to Image? possible name conflict (probably ok): import Image # from the PIL library
# I'll rename it.


# == ToggleAction

from __Symbols__ import stateref

ToggleAction = NamedLambda( ###e need to initialize the state if not there? NO, that's the job of the stateref (formula) itself!
    'ToggleAction',
    ((stateref, StateRef),),
    Set(stateref, not stateref) ### will 'not' be capturable by a formula?
        ## [update 061204: lhs and rhs are both wrong now, see Set.py -- lhs must be lval, rhs must be not stateref.value or so [nim]]
    )

# == ToggleButton

from __Symbols__ import stateref, false_icon, true_icon

ToggleButton = NamedLambda(
    'ToggleButton',
    ((stateref, StateRef),
     (false_icon, Image), #e add a default
     (true_icon, Image, false_icon), # same as false_icon, by default (default is a formula which can use prior symbols)
    ),
    Button(
        # plain image
        If(stateref,
           Overlay(Hidden(false_icon),Centered(true_icon)), # get the size of false_icon but the look of true_icon
               #e possible bugs: Centered might not work right if false_icon is not centered too; see also wrap/align options
               #e Overlay might work better outside, if otherwise something thinks the layout depends on the stateref state
           false_icon
        ),
        # highlighted image - ###e make this a lighter version of the plain image
        #e or a blue rect outlining the plain image -- I forget if Button assumes/implems the plain image always drawn under it...
        ###@@@ put this in somehow; missing things include my recollecting arg order of RectFrame, pixel units, dims of the icon, etc
        # actions -- for now, just do it immediately when pressed
        on_press = ToggleAction(stateref)
    ))

# == ToggleShow

ToggleFalseIcon = Rect(1,1,black) # stub
ToggleTrueIcon = Rect(1,1,gray) # stub

#e define default ToggleShow_stateref or StateRef value, in case env doesn't have one...

from __Symbols__ import thing, label, stateref

ToggleShow = NamedLambda(
    'ToggleShow',
    ((thing, Widget),
     (label, Widget, None),
     (stateref, StateRef, Automatic)),
        #e or should we specify a default stateref more explicitly? letting env override it as a feature of NamedLambda?
    Column( Row( ToggleButton(stateref, ToggleFalseIcon, ToggleTrueIcon),
                 label ),
            If( stateref, #k can you just plop in a stateref in place of asking for its value as a boolean? I guess so... it's a formula
                thing )
    ))

test_ToggleShow = ToggleShow( Rect(3,3,lightblue), "test_ToggleShow's label" )

#print test_ToggleShow

