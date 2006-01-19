#!/usr/bin/perl

 
$element{"H"} =  1;
$element{"He"} =  2;
$element{"Li"} =  3;
$element{"Be"} =  4;
$element{"B"} =  5;
$element{"C"} =  6;
$element{"N"} =  7;
$element{"O"} =  8;
$element{"F"} =  9;
$element{"Ne"} = 10;
$element{"Na"} = 11;
$element{"Mg"} = 12;
$element{"Al"} = 13;
$element{"Si"} = 14;
$element{"P"} = 15;
$element{"S"} = 16;
$element{"Cl"} = 17;
$element{"Ar"} = 18;
$element{"K"} = 19;
$element{"Ca"} = 20;
$element{"Sc"} = 21;
$element{"Ti"} = 22;
$element{"V"} = 23;
$element{"Cr"} = 24;
$element{"Mn"} = 25;
$element{"Fe"} = 26;
$element{"Co"} = 27;
$element{"Ni"} = 28;
$element{"Cu"} = 29;
$element{"Zn"} = 30;
$element{"Ga"} = 31;
$element{"Ge"} = 32;
$element{"As"} = 33;
$element{"Se"} = 34;
$element{"Br"} = 35;
$element{"Kr"} = 36;
$element{"Sb"} = 51;
$element{"Te"} = 52;
$element{"I"} = 53;
$element{"Xe"} = 54;

$bond{"-"} = "1";
$bond{"="} = "2";
$bond{"+"} = "3";
$bond{"@"} = "a";
$bond{"#"} = "g";

sub printbond {
    my($e1, $b1, $ec, $b2, $e2, %params) = @_;
    my($tmp);
    my($ktheta) = $params{"Ktheta"};
    my($theta0) = $params{"theta0"};
    my($CenterHybridization) = $params{"CenterHybridization"};

    if (!defined($element{$e1})) {
	print STDERR "strange element $e1\n";
	return;
    }
    if (!defined($element{$ec})) {
	print STDERR "strange element $ec\n";
	return;
    }
    if (!defined($element{$e2})) {
	print STDERR "strange element $e2\n";
	return;
    }
    if (!defined($bond{$b1})) {
	print STDERR "strange bond $b1\n";
	return;
    }
    if (!defined($bond{$b2})) {
	print STDERR "strange bond $b2\n";
	return;
    }

    $b1 = $bond{$b1};
    $b2 = $bond{$b2};

    if ($element{$e1} > $element{$e2} || ($e1 eq $e2 && $b1 gt $b2)) {
	$tmp = $e1;
	$e1 = $e2;
	$e2 = $tmp;
	$tmp = $b1;
	$b1 = $b2;
	$b2 = $tmp;
    }
#    print "addInitialBendData(\"$e1-$b1-$ec.$CenterHybridization-$b2-$e2\", $ktheta, $theta0);\n";
    print "addInitialBendData(\"$e1-$b1-$ec-$b2-$e2\", $ktheta, $theta0);\n";
}

while (<STDIN>) {
    # remove leading space, and trailing newline
    chomp;
    s/^\s+//;

    # ignore comments and blank lines
    if (/^#/) {
	next;
    }
    if (/^$/) {
	next;
    }

    if (/^(\S*)\s+(.*)$/) {
	$bond = $1;
	$rest = $2;
	%params = ();
	$params{"bond"} = $bond;
	$params{"CenterHybridization"} = "sp3" ;
	while ($rest =~ /^([^=]+)\s*\=\s*(\S+)\s*(.*)/) {
	    $key = $1;
	    $value = $2;
#	    print "$key = $value\n";
	    $rest = $3;
	    $params{$key} = $value;
	}
	if ($bond =~ /^(.*)([-=+@#])(.*)([-=+@#])(.*)$/) {
		$e1 = $1;
		$b1 = $2;
		$ec = $3;
		$b2 = $4;
		$e2 = $5;
		printbond($e1, $b1, $ec, $b2, $e2, %params);
	} else {
	    print STDERR "malformed bond: $_\n";
	}
    } else {
	print STDERR "unrecognized line: $_\n";
    }
}
