
// group.rl - Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

%%{
	
# Ragel definitions for the 'group' statement and related
	
	machine group;
	
	group_view_data_stmt_begin_line =
		'group' nonNEWLINEspace*
		'(' nonNEWLINEspace* 'View' nonNEWLINEspace+ 'Data' nonNEWLINEspace* ')'
		EOL
		@ { newViewDataGroup(); }
	;
	
	group_view_data_stmt_end_line =
		'egroup' nonNEWLINEspace*
		('(' nonNEWLINEspace* 'View'
		 nonNEWLINEspace+ 
		 'Data' nonNEWLINEspace* ')'
		)?
		EOL
		@ { endViewDataGroup(); }
	;
	
	group_view_data_stmt =
		group_view_data_stmt_begin_line
		IGNORED_LINE* :>
		group_view_data_stmt_end_line
	;
	
	end1_line = 'end1' EOL  @ { end1(); };
	
	group_clipboard_stmt_begin_line =
		'group' nonNEWLINEspace*
		'(' nonNEWLINEspace* 'Clipboard' nonNEWLINEspace* ')'
		EOL
		@ { newClipboardGroup(); }
	;
	
	group_clipboard_stmt_end_line =
		'egroup' nonNEWLINEspace*
		( '(' nonNEWLINEspace* 'Clipboard' nonNEWLINEspace* ')' )?
		EOL
		@ { endClipboardGroup(); }
	;
	
	group_clipboard_stmt =
		group_clipboard_stmt_begin_line
		IGNORED_LINE* :>
		group_clipboard_stmt_end_line
	;
	
	
	info_opengroup_line =
		'info' nonNEWLINEspace+ 'opengroup'
		(nonNEWLINEspace+  char_string_with_space  nonNEWLINEspace* '='
		 nonNEWLINEspace* char_string_with_space2)
		EOL
		@ { newGroupInfo(stringVal, stringVal2); }
	;
	
	group_mol_struct_stmt_begin_line =
		'group'
		% { stringVal2.clear(); }
		nonNEWLINEspace*
		'('  nonNEWLINEspace*  char_string_with_space  nonNEWLINEspace*  ')'
		(nonNEWLINEspace+ char_string_with_space2)?
		EOL
		@ { newMolStructGroup(stringVal, stringVal2); }
	;
	
	
	group_mol_struct_stmt_end_line =
		'egroup'
		% { stringVal.clear(); }
		( nonNEWLINEspace*
		  '('  nonNEWLINEspace*  char_string_with_space  nonNEWLINEspace*  ')'
		)?
		EOL
		@ { endMolStructGroup(stringVal); }
	;
	
	group_decl_line =
		'group'
		% { stringVal2.clear(); }
		nonNEWLINEspace+
		'('  nonNEWLINEspace*
		( ('View' nonNEWLINEspace+ 'Data') $(grouptype, 2) |
		  ('Clipboard') $(grouptype, 2) |
		  (char_string_with_space) $(grouptype, 1)
		)
		nonNEWLINEspace*  ')'
		(nonNEWLINEspace+ char_string_with_space2)?
		EOL
		@ { newMolStructGroup(stringVal, stringVal2); }
	;
	
	egroup_line =
		'egroup'
		% { stringVal.clear(); }
	( nonNEWLINEspace*
	  '('  (nonNEWLINEspace*  char_string_with_space  nonNEWLINEspace*)?  ')'
	)?
		EOL
		@ { endGroup(stringVal); }
	;
	
}%%
