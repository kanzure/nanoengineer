// molecule.rl - Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

%%{
# Ragel: definitions to recognize a molecule statement
	
	machine molecule;
	
	mol_decl_line = WHITESPACE**
		'mol'  nonNEWLINEspace+
		'('  nonNEWLINEspace*  char_string_with_space  nonNEWLINEspace* ')'
		(nonNEWLINEspace+ char_string_with_space2)?
		EOL
		>to { stringVal2.clear(); /* in case there is no 'style' string'*/ }
		@ {
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
		;
	
	
#	mol_stmt =
#		mol_decl_line
#		atom_stmt*
#		;
	
}%%
