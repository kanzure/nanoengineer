# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
'''
Dna_constants.py -- constants for Dna.

$Id: $

@see: References:
      - U{The Standard IUB codes used in NanoEngineer-1
        <http://www.idtdna.com/InstantKB/article.aspx?id=13763>}
      - U{http://en.wikipedia.org/wiki/DNA}
      - U{http://en.wikipedia.org/wiki/Image:Dna_pairing_aa.gif}

History:

2007-08-19 - Started out as part of Dna.py.
'''
__author__ = 'mark'

basesDict = { 'A':{'Name':'Adenine',    'Complement':'T',  'Basename':'Adenine' },
              'C':{'Name':'Cytosine',   'Complement':'G',  'Basename':'Cytosine'},
              'G':{'Name':'Guanine',    'Complement':'C',  'Basename':'Guanine' },
              'T':{'Name':'Thymine',    'Complement':'A',  'Basename':'Thymine' },
              'U':{'Name':'Uracil',     'Complement':'A',  'Basename':'Uracil'  },
              
              'X':{'Name':'Undefined',  'Complement':'X',  'Basename':''},
              'N':{'Name':'aNy base',   'Complement':'N',  'Basename':'aNy base'},
              
              'B':{'Name':'C,G or T',   'Complement':'V',  'Basename':''},
              'V':{'Name':'A,C or G',   'Complement':'B',  'Basename':''},
              'D':{'Name':'A,G or T',   'Complement':'H',  'Basename':''},
              'H':{'Name':'A,C or T',   'Complement':'D',  'Basename':''},
              
              'R':{'Name':'A or G (puRine)',     'Complement':'Y',  'Basename':''},
              'Y':{'Name':'C or T (pYrimidine)', 'Complement':'R',  'Basename':''},
              'K':{'Name':'G or T (Keto)',       'Complement':'M',  'Basename':''},
              'M':{'Name':'A or C (aMino)',      'Complement':'K',  'Basename':''},
              
              'S':{'Name':'G or C (Strong - 3H bonds)',  'Complement':'W', 'Basename':''},
              'W':{'Name':'A or T (Weak - 2H bonds)',    'Complement':'S', 'Basename':''} }

dnaDict = { 'A-DNA':{'DuplexRise':3.391},
            'B-DNA':{'DuplexRise':3.391},
            'Z-DNA':{'DuplexRise':3.715} }
 
# PAM5_AtomList contains the all PAM-5 base-pair atoms needed to construct any
# DNA structure. The four sets are:
#  -  startBasePair: The 5' set.
#  -    midBasePair: The middle set.
#  -    endBasePair: The 3' set.
#  - singleBasePair: A single set (properly terminated).
#
# The format:
#  - PAM5 Symbol, atom position, a_or_b (i.e. which strand the atom belongs to).
#
# Problems:
#  - Singlets must be added. These are needed to properly orient bondpoints 
#    between basepairs.
#  - Need bond pair list. Cannot create proper bonds between atoms with it.
#
# Special note:
#  This is a work in progress. I started this assuming it would be much
#  faster to make large PAM5 structures (like we have in origami) using 
#  constants like this rather than reading files. --Mark 2007-08-19

from VQT import V

PAM5_AtomList = {'PAM5BasePair':[ ("Pl", V( 8.699,  2.638,  1.590), "a"),
                                  ("Ss", V( 6.760,  0.0,    0.0  ), "a"),
                                  ("Ax", V( 0.0,    0.0,    0.0  ), " "),
                                  ("Ss", V(-4.610, -4.943,  0.0  ), "b"), 
                                  ("Pl", V(-7.863, -4.562, -1.590), "b") ] }