
// group.rl - Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

%%{
	
# Ragel definitions for the 'group' statement and related
#	
# NOTES:
#
# 1. Define the following variables in scope
#    char *lineStart;
#
# 2. Define the following functions in scope
#    void syntaxError(char *errorMessage);
	
	machine group;
	
	include utilities "utilities.rl";
	include atom "atom.rl";
	include molecule "molecule.rl";
	
	
	group_view_data_stmt_begin_line =
		'group'
		nonNEWLINEspace*
		> { lineStart = p; }
		'(' nonNEWLINEspace* 'View' nonNEWLINEspace+ 'Data' nonNEWLINEspace* ')'
		EOL
		@ { newViewDataGroup(); }
	;

	group_mol_struct_stmt_begin_line =
		'group'
		% { stringVal2.clear(); }
		nonNEWLINEspace*
		'('  nonNEWLINEspace*  char_string_with_space  nonNEWLINEspace*  ')'
		(nonNEWLINEspace+ char_string_with_space2)?
		nonNEWLINEspace*
		EOL
		@ { newMolStructGroup(stringVal, stringVal2); }
	;
	
	end1_line =
		'end1'
		nonNEWLINEspace*
		EOL
		@ { end1(); }
	;
	
	group_clipboard_stmt_begin_line =
		'group'   >{ lineStart = p; }
		nonNEWLINEspace*
		'(' nonNEWLINEspace* 'Clipboard' nonNEWLINEspace* ')'
		nonNEWLINEspace*
		EOL
		@ { newClipboardGroup(); }
	;
	
	egroup_line =
		'egroup'  >{lineStart=p;}
		% { stringVal.clear(); }
		( nonNEWLINEspace*
		'('  (nonNEWLINEspace*  char_string_with_space  nonNEWLINEspace*)?  ')'
		)?
		nonNEWLINEspace*
		EOL
		@ { endGroup(stringVal); }
	;
	
	info_opengroup_line =
		'info'   >{lineStart=p;} 
		nonNEWLINEspace+
		'opengroup'
		nonNEWLINEspace+
		char_string_with_space
		nonNEWLINEspace*
		'='
		nonNEWLINEspace*char_string_with_space2
		nonNEWLINEspace*
		EOL
		@ { newOpenGroupInfo(stringVal, stringVal2); }
	;
	
group_scanner :=
	|*
		#WHITESPACE* group_view_data_stmt_begin_line @(group,2);
		#WHITESPACE* group_clipboard_stmt_begin_line @(group,2);
		#WHITESPACE* group_mol_struct_stmt_begin_line @(group,1);
		WHITESPACE* group_mol_struct_stmt_begin_line;
		WHITESPACE* info_opengroup_line;
		WHITESPACE* egroup_line =>
			{ cerr << lineNum << ": returning from group" << endl; fret; };
		WHITESPACE* mol_decl_line;
		WHITESPACE* info_chunk_line;
		WHITESPACE* atom_decl_line;
		WHITESPACE* info_atom_line;
		WHITESPACE* bond_line;
		WHITESPACE* bond_direction_line;
	
		# skip blank and comment lines by providing no actions
		COMMENT_LINE;
		WHITESPACE* IGNORED_LINE =>
			{	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			};
	*|;
	
}%%
