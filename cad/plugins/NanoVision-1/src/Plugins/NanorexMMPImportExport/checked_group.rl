
// checked_group.rl - Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

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
	
	machine checked_group;
	
	include utilities "utilities.rl";
	include checked_atom "checked_atom.rl";
	include checked_molecule "checked_molecule.rl";
	
	
	checked_group_view_data_stmt_begin_line =
		'group'   > { lineStart = p; }
		nonNEWLINEspace*
		'(' nonNEWLINEspace* 'View' nonNEWLINEspace+ 'Data' nonNEWLINEspace* ')'
		EOL
		@ { newViewDataGroup(); }
		@lerr { syntaxError("Expecting the 'group (View Data)' statement"); }
	;
	
	checked_group_name =
		char_string_with_space
		@lerr { syntaxError("Badly formed group-name"); }
	;
	
	checked_group_style =
		char_string_with_space2
		@lerr { syntaxError("Badly formed group-style"); }
	;
	
	checked_group_mol_struct_stmt_begin_line =
		'group'   > {lineStart=p;}
# -- no style -- % { stringVal2.clear(); }
		nonNEWLINEspace*
		'('  nonNEWLINEspace*  checked_group_name  nonNEWLINEspace*  ')'
# -- no style -- (nonNEWLINEspace+ checked_group_style)?
		nonNEWLINEspace*
		EOL
		@ { newMolStructGroup(stringVal, stringVal2); }
	;
	
	
	checked_end1_line =
		'end1'   > {lineStart = p;}
		nonNEWLINEspace*
		EOL
		@ { end1(); }
		@lerr { syntaxError("Badly formed 'end1' statement"); }
	;
	
	checked_group_clipboard_stmt_begin_line =
		'egroup'  > {lineStart=p;}
		nonNEWLINEspace*
		'(' nonNEWLINEspace* 'Clipboard' nonNEWLINEspace* ')'
		EOL
		@ { newClipboardGroup(); }
		@lerr { syntaxError("Expecting the 'group (Clipboard)' statement"); }
	;
	
	
	checked_egroup_line =
		'egroup'   >{lineStart=p;}   % { stringVal.clear(); }
		nonNEWLINEspace*
		(  '('  (nonNEWLINEspace*  checked_group_name  nonNEWLINEspace*)?  ')'
		   nonNEWLINEspace*
		)?
		EOL
		@ { endGroup(stringVal); }
	;
	
	checked_info_opengroup_key =
		char_string_with_space
		@lerr { syntaxError("Badly formed 'info opengroup' key"); }
	;
	
	checked_info_opengroup_value =
		char_string_with_space2
		@lerr { syntaxError("Badly formed 'info opengroup' value"); }
	;
	
	checked_info_opengroup_line =
		'info'   >{lineStart=p;}
		nonNEWLINEspace+
		'opengroup'
		nonNEWLINEspace+
		checked_info_opengroup_key
		nonNEWLINEspace*
		'='
		nonNEWLINEspace*
		checked_info_opengroup_value
		nonNEWLINEspace*
		EOL
		@ { newOpenGroupInfo(stringVal, stringVal2); }
	;
	
	
checked_group_scanner :=
		|*
			WHITESPACE** checked_group_mol_struct_stmt_begin_line;
			WHITESPACE** checked_info_opengroup_line;
			WHITESPACE** checked_egroup_line =>
				{ cerr << lineNum << ": returning from group" << endl; fret; };
			WHITESPACE** checked_mol_decl_line;
			WHITESPACE** checked_info_chunk_line;
			WHITESPACE** checked_atom_decl_line;
			WHITESPACE** checked_info_atom_line;
			WHITESPACE** checked_bond_line;
			WHITESPACE** checked_bond_direction_line;
	
			# skip blank and comment lines by providing no actions
			WHITESPACE** COMMENT_LINE;
			IGNORED_LINE =>
				{   cerr << lineNum << ": Error : ";
					std::copy(ts, te, std::ostream_iterator<char>(cerr));
					cerr << endl;
				};
	*|;
	
}%%
