
%%{
	
# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
	
# NOTES:
#
#  1. Will need to 'include utilities "utilities.rl";' before including this file
#
#  2. Make declarations for the following variables visible in scope
#         int intVal, intVal2;
#         int x, y, z;
#         std::string stringVal, stringVal2;
#         int atomId, atomicNum;
#         char *lineStart;
#
#  3. Define the following functions
#         void newAtom(int atomId, int x, int y, int z, std::string const& atomStyle);
#         void newBond(std::string const& bondType, int targetAtomId);
#         void newBondDirection(int atomId1, int atomId2);
#         void newAtomInfo(std::string const& key, std::string const& value);
#         void syntaxError(std::string const& errorMessage);

	
	machine atom;
	
	atom_id =
		whole_number
		% { atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	;
	
	atomic_num =
		'(' nonNEWLINEspace* whole_number nonNEWLINEspace* ')'
		% { atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	;
	
	xcoord = nonNEWLINEspace*  integer  nonNEWLINEspace*  %{x = intVal; };
	ycoord = nonNEWLINEspace*  integer  nonNEWLINEspace*  %{y = intVal; };
	zcoord = nonNEWLINEspace*  integer  nonNEWLINEspace*  %{z = intVal; };
	
	
	atom_coords =
		'(' xcoord ',' ycoord ',' zcoord  ')'
#% { cerr << "atom_coords = (" << x << ',' << y << ',' << z << ')' << endl; }
		;
	
	
	atom_style =
		char_string_with_space
		% { atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	;
	

	atom_decl_line =
		'atom'
		nonNEWLINEspace+
		atom_id
		nonNEWLINEspace+
		atomic_num
		nonNEWLINEspace+
		atom_coords
		(nonNEWLINEspace+ atom_style)?
		nonNEWLINEspace*
		EOL
		@ { newAtom(atomId, atomicNum, x, y, z, atomStyle); }
		;
	
	
	action newBondAction {
		newBond(stringVal, intVal);
	}
	
	bond_line =
		'bond'
		[123acg] @ { stringVal = *p; }
		(nonNEWLINEspace+
		 whole_number
		 % newBondAction
		)+
		nonNEWLINEspace*
		EOL
		;
	
	
	action newBondDirectionAction {
		newBondDirection(intVal, intVal2);
	}
	
	bond_direction_line =
		'bond_direction'
		nonNEWLINEspace+
		whole_number
		nonNEWLINEspace+
		whole_number2
		nonNEWLINEspace*
		EOL
		@ newBondDirectionAction
		;
	
	action newInfoAtomAction {
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	
	info_atom_line =
		'info'
		nonNEWLINEspace+
		'atom'
		nonNEWLINEspace+
		char_string_with_space
		nonNEWLINEspace*
		'='
		nonNEWLINEspace*
		char_string_with_space2
		nonNEWLINEspace*
		EOL
		@ newInfoAtomAction
		;
	
	atom_attrib_line =
		(bond_line  |  bond_direction_line  |  info_atom_line);
	
	
}%%
