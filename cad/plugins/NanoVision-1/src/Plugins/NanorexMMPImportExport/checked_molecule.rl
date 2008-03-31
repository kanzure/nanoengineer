// checked_molecule.rl - Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

%%{

#! MACHINE molecule
#! Provides pattern definitions to recognize a molecule statement
#! Provides syntax-error checking
	
# NOTES:
# 1. Include the following lines before including this file
#        include utilities "utilities.rl";
	
	machine checked_molecule;
	
	checked_molecule_name =
		'('  nonNEWLINEspace*  char_string_with_space  nonNEWLINEspace* ')'
		@lerr { syntaxError("Badly formed molecule name"); }
	;
	
	checked_molecule_style =
		char_string_with_space2
		@lerr { syntaxError("Badly formed molecule style"); }
	;
	
	checked_mol_decl_line =
		'mol'  >{lineStart=p;}
		nonNEWLINEspace+    > { stringVal2.clear(); /* style is optional */ }
		checked_molecule_name
		(    nonNEWLINEspace+
		     checked_molecule_style
		)?
		nonNEWLINEspace*
		EOL
		@ {
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	;
	
	checked_info_chunk_key =
		char_string_with_space 
		$lerr { syntaxError("Badly formed key"); }
	;
	
	checked_info_chunk_value =
		char_string_with_space2
		$lerr { syntaxError("Badly formed value"); }
	;
	
	checked_info_chunk_line =
		'info'  >{lineStart=p;} 
		nonNEWLINEspace+
		'chunk'
		nonNEWLINEspace+
		checked_info_chunk_key
		nonNEWLINEspace*
		'='  $lerr { syntaxError("Expected '=' in assignment"); }
		nonNEWLINEspace*
		checked_info_chunk_value
		nonNEWLINEspace*
		EOL
		@ { newChunkInfo(stringVal, stringVal2); }
	;
	
}%%
