demo application readme file

@author: Bruce
@version: $Id$

requires: pyglet, which requires Python 2.4 and ctypes, or Python 2.5

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
