
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
		nonNEWLINEspace*
		EOL
		@ { newViewDataGroup(); }
	;

	csys_line =
		'csys'
		nonNEWLINEspace*
		'(' nonNEWLINEspace* char_string_with_space nonNEWLINEspace* ')'
		@ {csysViewName = stringVal;} # stringVal is reused in real_number patterns below
		nonNEWLINEspace*
		'('
		nonNEWLINEspace* real_number nonNEWLINEspace* ',' @{csysQw=doubleVal;}
		nonNEWLINEspace* real_number nonNEWLINEspace* ',' @{csysQx=doubleVal;}
		nonNEWLINEspace* real_number nonNEWLINEspace* ',' @{csysQy=doubleVal;}
		nonNEWLINEspace* real_number nonNEWLINEspace* ')' @{csysQz=doubleVal;}
		nonNEWLINEspace*
		'(' nonNEWLINEspace* real_number nonNEWLINEspace* ')' @{csysScale=doubleVal;}
		nonNEWLINEspace*
		'('nonNEWLINEspace* real_number nonNEWLINEspace* ',' @{csysPovX=doubleVal;}
		nonNEWLINEspace* real_number nonNEWLINEspace* ',' @{csysPovY=doubleVal;}
		nonNEWLINEspace* real_number nonNEWLINEspace* ')' @{csysPovZ=doubleVal;}
		nonNEWLINEspace*
		'(' nonNEWLINEspace* real_number nonNEWLINEspace* ')' @{csysZoomFactor=doubleVal;}
		nonNEWLINEspace*
		EOL
		@ { newNamedView(csysViewName, csysQw, csysQx, csysQy, csysQz, csysScale,
		                 csysPovX, csysPovY, csysPovZ, csysZoomFactor);
		}
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
		WHITESPACE* csys_line;
		WHITESPACE* group_mol_struct_stmt_begin_line =>
			{ fhold; fcall group_scanner; } ;
		WHITESPACE* info_opengroup_line;
		WHITESPACE* egroup_line => {fret;} ;
		WHITESPACE* mol_decl_line;
		WHITESPACE* info_chunk_line;
		WHITESPACE* atom_decl_line;
		WHITESPACE* info_atom_line;
		WHITESPACE* bond_line;
		WHITESPACE* bond_direction_line;
	
		# skip blank and comment lines by providing no actions
		COMMENT_LINE;
		WHITESPACE* IGNORED_LINE =>
			{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			};
	*|;
	
}%%
