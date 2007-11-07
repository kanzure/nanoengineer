#!/usr/bin/perl

# $Id$

use Switch;

# Check usage
#
if ($#ARGV < 1) {
  print "Usage: pylint_global.pl <pylint_global.txt> <Pylint.result>\n";
  exit;
}

$inFile = $ARGV[0];
$batchNumber = $ARGV[1];
$outFile = $ARGV[2];

$A_F_link = "<a href=\"pylint_global.0.html\">A-F</a>";
$G_L_link = "<a href=\"pylint_global.1.html\">G-L</a>";
$M_R_link = "<a href=\"pylint_global.2.html\">M-R</a>";
$S_X_link = "<a href=\"pylint_global.3.html\">S-X</a>";
$Y_Z_link = "<a href=\"pylint_global.4.html\">Y-Z</a>";

$exprs_link = "<a href=\"pylint_global.5.html\">exprs</a>";
$PM_link = "<a href=\"pylint_global.6.html\">PM</a>";
$startup_link = "<a href=\"pylint_global.7.html\">startup</a>";
$utilities_link = "<a href=\"pylint_global.8.html\">utilities</a>";

print "<h3>Pylint Results<br>\n";
print "<font style=\"font-size: small; font-weight: normal\">Back to the <a href=\"/Engineering/\">SEMBot</a></font>\n";
print "<br><font style=\"font-size: small; font-weight: normal\">(time/version stamp could go here)</font>";
print "</h3>\n";
print "<p>\n";
print "Module Batches<br>\n";
switch ($batchNumber) {
  case 0 { print "<b>A-F</b> | $G_L_link | $M_R_link | $S_X_link | $Y_Z_link"; }
  case 1 { print "$A_F_link | <b>G-L</b> | $M_R_link | $S_X_link | $Y_Z_link"; }
  case 2 { print "$A_F_link | $G_L_link | <b>M-R</b> | $S_X_link | $Y_Z_link"; }
  case 3 { print "$A_F_link | $G_L_link | $M_R_link | <b>S-X</b> | $Y_Z_link"; }
  case 4 { print "$A_F_link | $G_L_link | $M_R_link | $S_X_link | <b>Y-Z</b>"; }
  else   { print "$A_F_link | $G_L_link | $M_R_link | $S_X_link | $Y_Z_link"; }
}
print "<p>\n";
print "Packages<br>\n";
switch ($batchNumber) {
  case 5 { print "<b>exprs</b> | $PM_link | $startup_link | $utilities_link"; }
  case 6 { print "$exprs_link | <b>PM</b> | $startup_link | $utilities_link"; }
  case 7 { print "$exprs_link | $PM_link | <b>startup</b> | $utilities_link"; }
  case 8 { print "$exprs_link | $PM_link | $startup_link | <b>utilities</b>"; }
  else   { print "$exprs_link | $PM_link | $startup_link | $utilities_link"; }
}

print "<pre>\n";

$fragOpen = 0;
open (INFILE, $inFile) || die "Can't open $inFile: $!\n";
while ($line = readline(INFILE)) {
  if ($fragOpen == 1) {
    if ($line =~ /Messages/) {
      $fragOpen = 0;
      print $line

    } else {
      # |atombasetests        |53.14 |11.21   |27.52    |6.53       |
      if ($line =~ /^\|(\S+)(\s+.+)/) {
        print "|<a href=\"pylint_$1.txt\">$1</a>$2\n";
		#&sortMessages($1)

      } else {
        print $line
      }
    }

  } else {
    # |module   |error |warning |refactor |convention |
    if ($line =~ /^\|module\s+\|error/) {
      $fragOpen = 1;

    } elsif ($line =~ /Your code has been rated at (\S+)\//) {
      $outFile = "> $outFile";
      open (OUTFILE, $outFile) || die "Can't open $outFile for writing: $!\n";
      print OUTFILE $1;
      close (OUTFILE);
    }
    print $line
  }
}

print "</pre>\n";

unlink"tmp.txt";



#
# SUBROUTINE: sortMessages
#
# TODO: This needs to keep the code snipits associated with some lines, with
#       the line.
#
sub sortMessages {
  local ($module) = pop(@_);

  system "sort -r -k 2 SVN-D/cad/src/pylint_$module.txt > tmp.txt";
  system "mv tmp.txt SVN-D/cad/src/pylint_$module.txt";
}

