#!/usr/bin/perl

# Check usage
#
if ($#ARGV < 1) {
  print "Usage: pylint_global.pl <pylint_global.txt> <Pylint.result>\n";
  exit;
}

$inFile = $ARGV[0];
$outFile = $ARGV[1];

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
      } else {
        print $line
      }
    }

  } else {
    # |module   |error |warning |refactor |convention |
    if ($line =~ /^\|module\s+\|error/) {
      $fragOpen = 1;

    } elsif ($line =~ /Your code has been rated at (\S+)/) {
      $outFile = "> $outFile";
      open (OUTFILE, $outFile) || die "Can't open $outFile for writing: $!\n";
      print OUTFILE $1;
      close (OUTFILE);
    }
    print $line
  }
}

print "</pre>\n"

