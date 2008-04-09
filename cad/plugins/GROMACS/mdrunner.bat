
set GMXLIB=%1
%2 -s %3.tpr -o %3.trr -e %3.edr -c %3-out.gro -g %3-mdrun.log %4 %5 >%3-mdrun-stdout.txt 2>%3-mdrun-stderr.txt
