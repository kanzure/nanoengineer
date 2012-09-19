#! /usr/bin/env python

"""
This file, and some of the files in the same directory and/or its subdirs,
are copied and modified from delta_v-r3/run_game.py and/or other programs
by Alex H., author of pyglet. Each such file says so inside it.
"""

import sys

import optparse

import pyglet

from demoapp.ui.DemoAppWindow import DemoAppWindow

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-W', '--width', dest='width', type='int', default = 800,
                  help='width of window')
    op.add_option('-H', '--height', dest='height', type='int', default = 600,
                  help='height of window')
    op.add_option('-f', '--fullscreen', dest='fullscreen', default = False,
                  action='store_true', help='use an entire screen')
    options, args = op.parse_args()

    # In case the user doesn't run in -O
##    pyglet.options['gl_error_check'] = False

    if options.fullscreen:
        window = DemoAppWindow( fullscreen = options.fullscreen)
    else:
        window = DemoAppWindow(
                              width = options.width,
                              height = options.height,
                             )
##    state = mainmenu.MainMenu()
##    window.push_state(state)

    pyglet.app.run()
