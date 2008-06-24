#!/usr/bin/env gawk -f
#
# indent-diff.gawk -- Filter indentation changes from context diffs.
#    Only diff line groups with indentation changes are printed.
#
#   Indentation is significant for control structures in Python code.
#   On matching change lines (starting with a "!" in context diffs),
#   if the indentation is different, the indentation count is inserted
#   after the "! " to highlight the change.  e.g:
#
#      ***************
#      *** 33,35 ****
#                    draw_vane( bond, a1py, a2py, ord_pi_y, rad, col)
#      !  8      if ord_pi_z:
#                    draw_vane( bond, a1pz, a2pz, ord_pi_z, rad, col) 
#      --- 33,35 ----
#                    draw_vane( bond, a1py, a2py, ord_pi_y, rad, col)
#      ! 12          if ord_pi_z:
#                    draw_vane( bond, a1pz, a2pz, ord_pi_z, rad, col) 
#
#   Note: Tab characters go to 8-space tab stops, as Python assumes.

BEGIN {
    debug = 0 ## 1
    # Minimum indentation difference to report.
    mindiff = 2
}

# Capture the file header lines.
/^\*\*\* [a-zA-Z]/ {
    if ( entry ) doGroup(); entry = 0;
    ofile = $0;
    didHdr = 0;
    if ( debug ) print "Starting", ofile;
    next;
}
/^\-\-\- [a-zA-Z]/ { nfile = $0; next; }

# Collect and process diff line groups.
# Line group separator.
/^\*\*\*\*\*\*/ {
    if ( entry ) doGroup();
    entry = 1; oline = 1; nline = 0;
}
# Separator between old and new line sections.
/^--- [1-9]/ { nline = 1; }
# Store lines.
{ if ( nline ) nlines[nline++] = $0; else olines[oline++] = $0; next; }
END { if ( entry ) doGroup(); }

# Process a diff line group within a file diff.
function doGroup() {
    # Compare the indentation on old and new lines in a line group.
    nonmatches = 0;
    for ( o = n = 1; o < oline && n < nline; o++ ) {
        osig = sig( ol = olines[o] );
        # Ignore old, non-change ("!") lines.
        if ( substr(ol, 1, 1) != "!" ) continue;
        # Look for a corresponding new change line.
	nonmatched = 1;
        oind = indLen(ol);
        for ( ; n < nline; n++ ) {
            nsig = sig( nl = nlines[n] );
	    ##printf "sigs\n  %s|%s\n  %s|%s\n", osig, ol, nsig, nl;
            # Ignore new, non-change ("!") lines.
            if ( substr(nl, 1, 1) != "!" ) continue;
            if ( nsig != osig ) {
	        if ( debug ) printf "different signatures\n  %s\n  %s\n", ol, nl;
	    } else {
                # Matching signatures, compare indentation.
                nind = indLen(nl);
                if ( nind <= (oind + mindiff) && nind >= (oind - mindiff)  ) {
		    if ( debug ) \
			printf "%s %d/%d\n  %s\n  %s\n", \
			    "matched sigs & indentation", oind, nind, ol, nl;
		    nonmatched = 0;
		}
		else {
		    # Non-match: Insert indentation lengths to show where.
		    olines[o] = substr(olines[o], 1, 2) sprintf("%2d", oind) \
				substr(olines[o], 5);
		    nlines[n] = substr(nlines[n], 1, 2) sprintf("%2d", nind) \
				substr(nlines[n], 5);
		    if ( debug ) \
			printf "Different indentation %d/%d\n  %s\n  %s\n", \
			    oind, nind, olines[o], nlines[n]
		}
		n++;   # Matched signatures, go on to next line.
	        break; # Out of the new-line loop.
            }
	}
	nonmatches += nonmatched
    }

    # Print line groups with indentation that isn't known to match.
    if ( nonmatches ) {
        if ( ! didHdr ) { print ofile; print nfile; didHdr = 1; }
	for ( o = 1; o < oline; o++ ) print olines[o];
	for ( n = 1; n < nline; n++ ) print nlines[n];
    }
}

# Use the first two words on the line as a signature.
function sig(line) {
    notWord = "[^a-zA-Z0-9_]+";
    word = "([a-zA-Z0-9_]+)";
    twoWords = "^" notWord word notWord word ".*";
    oneWord = "^" notWord word ".*";
    ret = gensub(twoWords, "\\1 \\2", 1, line);

    # There may not be two words on the line, or any.
    if ( ret == line ) ret = gensub(oneWord, "\\1", 1, line);
    if ( ret == line ) ret = ""

    ##print "sig", match(line, pat), ret
    return ret;
}
    
# The length of indentation on a line in a context diff entry.
function indLen(line) {
    # Whitespace from the beginning of the line.
    # Skip the first two characters, which are prefixed by diff.
    ws = gensub("..([ \t]*).*", "\\1", 1, line);
    ##print "wslen=", length(ws), " ws='" ws "'"

    # Convert tabs to spaces using 8-space tab stops, as Python assumes.
    spaces = 0
    for (i = 1; i <= length(ws); i++) {
        if (substr(ws, i, 1) == " ") spaces++;
	else spaces += 8 - spaces % 8;
	##print spaces;
    }

    return spaces;
}

