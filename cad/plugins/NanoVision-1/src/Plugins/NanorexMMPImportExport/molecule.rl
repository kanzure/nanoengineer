// molecule.rl - Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

%%{
# Ragel: definitions to recognize a molecule statement
	
	machine molecule;
	
	mol_decl_line = WHITESPACE**
		'mol'  >{lineStart=p;}
		nonNEWLINEspace+
			>to { stringVal2.clear(); /* 'style' string optional */ }
		'('  nonNEWLINEspace*  char_string_with_space  nonNEWLINEspace* ')'
		(nonNEWLINEspace+ char_string_with_space2)?
		nonNEWLINEspace*
		EOL
		@ {
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
		;
	
	info_chunk_line =
		'info'   >{lineStart=p;}
		nonNEWLINEspace+
		'chunk'
		nonNEWLINEspace+
		char_string_with_space
		nonNEWLINEspace*
		'='
		nonNEWLINEspace*
		char_string_with_space2
		nonNEWLINEspace*
		EOL
		@ { newChunkInfo(stringVal, stringVal2); }
		;

}%%
