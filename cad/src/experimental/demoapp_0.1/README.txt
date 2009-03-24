demo application readme file

@author: Bruce
@version: $Id$

requires: pyglet, which requires Python 2.4 and ctypes, or Python 2.5 or 2.6

(demoapp has been tested with pyglet versions 1.1beta2 and 1.1.2, and Python 2.5)

==

Installation:

- make sure typing 'python' at the shell command line runs Python 2.4 or 2.5 or 2.6

- if it runs Python 2.4, install ctypes

- install pyglet from pyglet.org in one of two ways:

  - follow its instructions to make pyglet part of your standard installation
    of the same python which is run by 'python' from your shell command line
    
  - or, link to the source code of pyglet (already in a directory called 'pyglet')
    from this directory, e.g.
    
    % ln -s <somewhere>/pyglet-1.1beta2/pyglet pyglet
    
  In the latter case, the local pyglet will be used, overriding one in your
  Python installation (if any).

==

Running:

% python main.py

==

Usage (while running): not documented except (incompletely) in the source code.

(It's not useful as a program anyway, just a source code example.)

==

some useful commands (to be run in this directory):

% make clean

% python main.py  [this directory must be current, or must be on the python path]

% ./bak.sh 080613-morn

and if you have nanorex cad/src at $W:

% $W/tools/Refactoring/RenameModule.py scratch.py DemoAppWindow.py
% mv scratch.py DemoAppWindow.py

% mkdirs demoapp/ui
% touch demoapp/ui/__init__.py
% $W/tools/Refactoring/RenameModule.py DemoAppWindow.py demoapp/ui/
% mv DemoAppWindow.py demoapp/ui/

the last two lines of that can be abbreviated as:

% ./put.sh DemoAppWindow.py ui
