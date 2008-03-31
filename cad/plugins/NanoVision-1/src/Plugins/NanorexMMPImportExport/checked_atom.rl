// checked_atom.rl - Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

%%{
	
# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
	
# NOTES:
#
#  1. Will need to include the following statements before including this file
#         include utilities "utilities.rl";
#
#  2. Make declarations for the following variables visible in scope
#         char *lineStart;
#
#  3. Define the following functions
#         void syntaxError(std::string const& errorMessage);
	
	
#! MACHINE: checked_atom
#! Provides Ragel patterns for recognizing atom declaration lines and provides
#!     syntax-error checking
	
	machine checked_atom;
	
	include atom "atom.rl";
	
	
	checked_atom_id =
		atom_id
		@lerr { syntaxError("Badly formed integer"); }
	;
	
	checked_atomic_num =
		atomic_num
		@lerr { syntaxError("Badly formed atomic number"); }
	;
	
	checked_atom_coords =
		'(' xcoord ',' ycoord ',' zcoord  ')'
#% { cerr << "atom_coords = (" << x << ',' << y << ',' << z << ')' << endl; }
		@lerr { syntaxError("Badly formed coordinates"); }
	;
	
	
	checked_atom_style =
		char_string_with_space
		% { atomStyle = stringVal;
/*cerr << "atom_style = " << stringVal << endl;*/
		}
		@lerr { syntaxError("Badly formed atom-style specification"); }
	;
	
	
	checked_atom_decl_line =
		'atom'  >{lineStart=p;} nonNEWLINEspace+
		checked_atom_id  nonNEWLINEspace+
		checked_atomic_num  nonNEWLINEspace+
		checked_atom_coords
		(nonNEWLINEspace+ checked_atom_style)?
		nonNEWLINEspace*
		EOL
		@ { newAtom(atomId, atomicNum, x, y, z, atomStyle); }
# no error actions because each component supplies its own
	;
	
	
	checked_bond_type =
		[123acg]
		@ { stringVal = *p; }
		@lerr { syntaxError("Invalid bond-specification - " + stringVal); }
	;
	
	checked_bond_target_atom_id =
		whole_number
		% newBondAction
		@lerr { syntaxError("Invalid bond-target atom id"); }
	;
	
	checked_bond_line =
		'bond'  >{lineStart=p;}
		checked_bond_type
		(nonNEWLINEspace+  checked_bond_target_atom_id)+
		nonNEWLINEspace*
		EOL;
	
	
	checked_bond_direction_line =
		'bond_direction'  >{lineStart=p;}
		nonNEWLINEspace+
		whole_number
			$lerr { syntaxError("Invalid bond-direction specification"); }
		nonNEWLINEspace+
		whole_number2
			$lerr { syntaxError("Invalid bond-direction specification"); }
		nonNEWLINEspace*
		EOL
		@ newBondDirectionAction;
	

	checked_info_atom_line =
		'info'  >{lineStart=p;}
		nonNEWLINEspace+   'atom'
		nonNEWLINEspace+   char_string_with_space
			$lerr{ syntaxError("Badly formed key"); }
		nonNEWLINEspace*  '='
			$lerr { syntaxError("Expecting '=' after key"); }
		nonNEWLINEspace*   char_string_with_space2
			$lerr{ syntaxError("Badly formed value"); }
		nonNEWLINEspace*
		EOL
		@ newInfoAtomAction
		;
	
	checked_atom_attrib_line =
		( checked_bond_line            |
		  checked_bond_direction_line  |
		  checked_info_atom_line
		);
	
}%%
