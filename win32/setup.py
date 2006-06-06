# setup.py
from distutils.core import setup
import py2exe

opts = { "py2exe": {"excludes": "OpenGL",	
			  "includes": "sip",
		   }
       } 
      
setup(options = opts,
     windows=["atom.py"])