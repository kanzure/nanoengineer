# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PovrayScenePropDialog.ui'
#
# Created: Fri Jun 9 10:45:12 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x02" \
    "\x5d\x49\x44\x41\x54\x38\x8d\xad\x94\x5f\x48\x93" \
    "\x51\x18\xc6\x7f\x5b\x6d\xe6\xe6\xe6\x37\xa3\x62" \
    "\x73\xe8\xa2\x61\x16\x96\x65\x7f\xee\x6c\x43\xba" \
    "\x49\x24\xcc\xc0\x9b\x2e\xec\xa2\x90\x20\x4c\x0a" \
    "\xf1\xce\x31\x09\xb1\xa0\x8b\xba\x28\x0b\x8c\x40" \
    "\x28\xfb\x87\xa3\x2b\x43\xa8\xcf\x29\x89\x50\x22" \
    "\x5e\xe4\x8d\xc1\xa2\x64\x20\x2b\xbe\xe9\xb6\x8f" \
    "\xf5\xa5\xa7\x8b\xe1\x10\xbf\xe5\x04\x7d\xe0\x5c" \
    "\x1c\xce\x79\x7e\xbc\xcf\x7b\x0e\x2f\x6c\xb3\x0c" \
    "\x6b\x37\x81\xae\x80\xd8\xac\x31\xd8\x1d\xd4\xf9" \
    "\x75\x0a\x74\x05\xc4\x7a\x45\x14\x21\xe4\x88\x10" \
    "\x4a\x32\x2e\x94\x64\x5c\xac\xfc\xcd\x2c\x59\xfe" \
    "\x28\x00\x5d\x01\x3b\xff\x07\xbf\x3f\xb1\x42\x7b" \
    "\x53\x07\x38\xac\x10\xfd\x0e\x95\x17\x33\x07\x67" \
    "\x6a\x01\x90\xeb\x0d\xc8\xb2\x8c\xdf\xef\x17\x6b" \
    "\x2b\xcd\x09\xbc\xda\xfb\x0a\xa7\x3a\x8b\x88\xde" \
    "\x43\x2c\x2f\x22\x62\x31\x46\x46\x07\x01\x18\x9f" \
    "\x9e\xe0\xf6\xa3\x61\xfc\x77\xa7\xd7\x5a\xb2\x50" \
    "\x1d\x30\x9e\x5a\xe4\xda\x59\x2f\x35\x27\x9b\x99" \
    "\x9a\x1c\xe3\xc4\xc0\x29\xc0\x45\xa3\xd5\x09\xc0" \
    "\xf9\x4a\x27\xa3\xcf\x2a\xf0\x75\xce\x70\xd4\x57" \
    "\xcd\x78\x6f\x1d\xf6\x92\xf2\xac\xdf\x98\xab\xc2" \
    "\x9a\x63\x07\x98\x9a\x1c\xe3\xe6\xf3\x39\xb0\xaa" \
    "\xd8\xac\x51\x42\x7d\x43\x84\xfa\x86\xc0\xba\x1b" \
    "\x4f\x85\x97\xd2\x83\x25\xcc\x84\xc3\x3a\x6f\xce" \
    "\xc8\x31\x45\xc3\x21\x15\x13\x6c\xd8\x83\xbf\xa1" \
    "\x91\x25\x47\x21\x2c\xbe\xa7\xe3\x7a\x2b\x2d\xbe" \
    "\x2a\x00\xe6\x29\x43\x32\x7f\x26\xb6\xa0\xe4\x07" \
    "\x46\xa3\x51\x8e\x1c\x2a\xa7\x6e\xd0\xce\xd0\x93" \
    "\x26\x42\xc3\x32\x6d\x97\x5f\x03\xf0\x70\x74\x9e" \
    "\x91\xd9\xdf\x30\xfc\x94\xf6\xce\x1a\x7e\xe4\x03" \
    "\x6a\xa9\x3f\x68\x29\x85\xda\x2b\x21\x22\x05\x2d" \
    "\x5c\x78\x11\xa1\x76\xbf\x0d\x7f\xcf\x27\x00\x96" \
    "\xc2\x6f\x00\xb8\xd1\x5a\x47\xd5\xe1\xe3\xf9\x23" \
    "\xab\xaa\x8a\xc7\xeb\xa5\xe4\x74\x29\xc8\xdf\xb0" \
    "\x2d\xbc\x25\xb1\xaf\x9a\x26\xd7\x12\x00\xbe\xfe" \
    "\x60\xc6\xb8\x03\x4c\x16\x89\xa2\xc2\xa2\xfc\x91" \
    "\xe3\x69\x78\xf7\x65\x05\xc2\x77\x78\xd0\x73\x0b" \
    "\x9b\xe4\x20\x95\x5e\x06\x40\x18\x32\xef\x58\x2c" \
    "\x39\x70\xbb\xdc\x98\x0a\x4c\xf9\x81\xf2\x5c\x1a" \
    "\xbe\x4e\xd3\xde\xb8\x17\xa3\x45\xc2\x64\x91\x28" \
    "\x73\xda\x01\xb0\x59\xed\xd9\x7b\xa6\x02\x13\x5a" \
    "\x5a\xdb\x18\x68\x31\x1b\x99\x89\x81\x94\x1a\xa0" \
    "\xfe\xdc\x25\x54\xc3\x2e\xdc\x2e\x37\x76\xc9\x9e" \
    "\x6d\x09\xa0\x03\xad\x2a\xe7\x3f\xdc\x8a\x74\x40" \
    "\xb3\x79\x99\xfe\x97\x1f\x08\x3f\x6e\xe3\xe7\xaf" \
    "\x64\xb6\x4f\xaa\xaa\xa2\xaa\x2a\x5a\x5a\x43\x4b" \
    "\x6b\x39\xe3\x42\x8e\xc8\x4a\xc2\x40\x77\xbd\x44" \
    "\x2c\x69\xc4\x53\xee\xc9\x36\x7d\xbd\x79\x75\x9f" \
    "\x50\x13\x1b\x57\xb8\x55\xad\x1f\x90\x9b\x1e\xb0" \
    "\x9b\x60\x6d\x8f\xfe\x01\x95\xbb\xf0\xe5\x6b\xf5" \
    "\x0a\x96\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42" \
    "\x60\x82"
image1_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x02" \
    "\x60\x49\x44\x41\x54\x38\x8d\xd5\x94\x4f\x48\x93" \
    "\x61\x1c\xc7\x3f\x5b\x6d\xe6\xe6\xe6\x3b\xa3\x62" \
    "\x73\xe8\xa2\x61\x16\x96\x65\x7f\x6e\xb6\x21\x5d" \
    "\x12\x09\x33\xe8\xd2\xc1\x0e\x85\x04\x61\x52\x88" \
    "\x37\xc7\x24\xc4\x82\x0e\x75\x28\x0b\x8c\x40\x28" \
    "\xfb\x87\xa3\x93\x21\xd4\xeb\x94\x44\x28\x11\x0f" \
    "\x79\x31\x58\x94\x0c\x64\xc5\x3b\xdd\xf6\xb0\xde" \
    "\xf4\xed\x30\x94\x1c\xef\xe2\x85\xba\xf8\x85\xe7" \
    "\xf0\xfc\xf9\x7e\x9e\x1f\xdf\xdf\xc3\x03\x9b\x4d" \
    "\xa6\xfc\x85\x50\x77\x48\x33\x6a\x0e\xf7\x84\x75" \
    "\x19\xba\x0a\x75\x87\xb4\x7c\xc5\x14\x4d\x93\x63" \
    "\x9a\xa6\xa4\x93\x9a\x92\x4e\x6a\xab\xbf\x72\x43" \
    "\x96\xdf\x69\x80\x6e\x21\x5b\xff\x76\xc9\x9d\xc9" \
    "\x55\x3a\x5a\x3a\xc1\x65\x87\xf8\x17\xa8\x3e\x9b" \
    "\xdb\x38\x51\x0f\x80\xdc\x68\x42\x96\x65\x82\xc1" \
    "\xa0\x96\x5f\x79\x41\xf0\xa5\xbe\xe7\xb8\xc5\x1c" \
    "\x5a\xfc\x36\xda\xca\x12\x5a\x22\xc1\xe8\xd8\x10" \
    "\x00\x13\x33\x93\xdc\xb8\x3f\x42\xf0\xd6\xcc\x9f" \
    "\x96\x0d\x70\x5d\x70\x32\xb3\xc4\xe5\x93\x7e\xea" \
    "\x8e\x9e\x63\x7a\x6a\x9c\x23\x83\xc7\x00\x0f\xcd" \
    "\x76\x37\x00\xa7\xab\xdd\x8c\x3d\xae\x22\xd0\x35" \
    "\xcb\xc1\x40\x2d\x13\x7d\x0d\x38\xcb\x2a\x37\x30" \
    "\xcc\x85\x2a\xae\x3b\xb4\x87\xe9\xa9\x71\xae\x3d" \
    "\x99\x07\xbb\xc0\x61\x8f\x13\xe9\x1f\x26\xd2\x3f" \
    "\x0c\xf6\xed\xf8\xaa\xfc\x94\xef\x2d\x63\x36\x1a" \
    "\xd5\xf5\x17\x8c\x22\xa1\xa8\xb8\xa4\x52\xc2\x4d" \
    "\x3b\x08\x36\x35\xb3\xec\x2a\x86\xa5\x37\x74\x5e" \
    "\x69\xa3\x35\x50\x03\xc0\x02\x15\x48\xd6\x0f\x24" \
    "\x16\x15\xe3\xe0\x78\x3c\xce\x81\x7d\x95\x34\x0c" \
    "\x39\x19\x7e\xd8\x42\x64\x44\xa6\xfd\xc2\x0b\x00" \
    "\xee\x8d\x2d\x30\x3a\xf7\x03\x46\x1e\xd1\xd1\x55" \
    "\xc7\x57\xa3\x60\x35\xf3\x13\x35\xa3\x50\x7f\x31" \
    "\x42\xac\xa8\x95\x33\x4f\x63\xd4\xef\x76\x10\xec" \
    "\x7d\x0f\xc0\x72\xf4\x25\x00\x57\xdb\x1a\xa8\xd9" \
    "\x7f\xd8\x78\x14\x42\x08\x7c\x7e\x3f\x65\xc7\xcb" \
    "\x41\xfe\x8c\x63\xf1\x15\xa9\x5d\xb5\xb4\x78\x96" \
    "\x01\x08\x0c\x84\x73\xe6\x2d\x60\xb1\x49\x94\x14" \
    "\x97\x18\x8f\x22\x99\x85\xd7\x1f\x57\x21\x7a\x93" \
    "\xbb\xbd\xd7\x71\x48\x2e\x32\xd9\x15\x00\x34\x53" \
    "\xae\xe7\xa5\x92\x0b\xaf\xc7\x8b\xa5\xc8\x62\x1c" \
    "\x2c\xcf\x67\xe1\xd3\x0c\x1d\xcd\x3b\x31\xdb\x24" \
    "\x2c\x36\x89\x0a\xb7\x13\x00\x87\xdd\xb9\x7e\xce" \
    "\x52\x64\x41\xcd\xaa\xc6\xc0\x36\xab\x99\xd9\x04" \
    "\x48\x99\x41\x1a\x4f\x9d\x47\x98\xb6\xe1\xf5\x78" \
    "\x71\x4a\x39\xa0\x10\x02\x40\x17\xb8\xa6\x82\xef" \
    "\xf8\x5f\xa5\x0b\xb6\x5a\x57\x18\x78\xf6\x96\xe8" \
    "\x83\x76\xbe\x7d\x4f\xaf\xe7\x28\x84\x40\x08\x81" \
    "\x9a\x55\x51\xb3\x6a\xc1\x18\xa0\x40\x14\x4a\xca" \
    "\x44\x4f\xa3\x44\x22\x6d\xc6\x57\xe9\x5b\x6f\x4e" \
    "\x3e\x64\x6d\x9e\x12\x29\x63\x15\xff\x0f\xe9\x7d" \
    "\xd2\x86\x3f\x7a\x83\xbc\x4d\xa2\xdf\x6d\x04\xf0" \
    "\xe5\x28\xc0\xea\x2d\x00\x00\x00\x00\x49\x45\x4e" \
    "\x44\xae\x42\x60\x82"
image2_data = [
"135 40 764 2",
"i0 c #045d95",
"jQ c #0467a6",
"jU c #055e96",
"jT c #05629e",
"i4 c #0564a0",
"i5 c #0566a4",
"jJ c #0768a5",
"jN c #0769a6",
"jI c #0769a7",
"jb c #0a6aa7",
"ir c #0a6ba8",
"j. c #0b5f95",
"i8 c #0b659d",
"i9 c #0b6ba8",
"iv c #0b6ca8",
"iu c #0c6398",
"iE c #0d68a2",
"iD c #0e6399",
"iy c #0e6ca9",
"iz c #0e6da9",
"i3 c #0f5b8b",
"bO c #105b8a",
"i# c #106da8",
"i. c #106eaa",
"hX c #106faa",
".P c #115987",
".O c #116499",
".U c #11669b",
"hZ c #116faa",
"hs c #136397",
"hq c #136ba2",
"hv c #136ea8",
"hr c #1370ab",
".V c #165a7d",
"hw c #166394",
"g9 c #1670a9",
"g5 c #1672ac",
"hm c #1772ac",
"hn c #1773ac",
"#9 c #185f8d",
"jc c #19608d",
"jY c #19638f",
"gT c #1972aa",
"gS c #1974ad",
"gU c #1a5a82",
"jR c #1a5c86",
"jZ c #1a618b",
"j1 c #1a638f",
"a3 c #1a75ad",
"g8 c #1b6695",
"a2 c #1b6a9a",
"gC c #1b6c9f",
"#7 c #1b71a7",
"#8 c #1b75ae",
"jX c #1c5c83",
"gA c #1c73a9",
"gZ c #1c76ae",
"jM c #1d628d",
"#Y c #1d6a9a",
"g2 c #1d76ae",
"gB c #1d76af",
"jH c #20638e",
"#W c #2077ae",
"#X c #2078af",
"gf c #2078b0",
"a4 c #215a7e",
"h9 c #216691",
"iA c #226087",
"f2 c #2277ab",
"gL c #2279b0",
"gO c #237ab0",
"f1 c #237ab1",
"gR c #246a95",
"h0 c #266a94",
"aP c #2772a0",
"fJ c #2775a5",
"fL c #28668c",
"gr c #287db2",
".C c #297aad",
".I c #297db1",
"gu c #297eb2",
"fK c #297eb3",
"g6 c #2a668a",
"bN c #2a698f",
".D c #2a7eb3",
".N c #2b644a",
".E c #2b677f",
"fl c #2b77a6",
"aO c #2b80b3",
"g# c #2e81b4",
"fm c #2f81b4",
"fk c #2f82b5",
"e3 c #3077a3",
"bP c #316888",
"gV c #316b8e",
"#T c #3283b5",
"#S c #3283b6",
"e2 c #337ca9",
"fX c #3382b3",
"ib c #346d90",
"aB c #3477a1",
"e0 c #3478a1",
"fY c #3482b3",
"fW c #3483b4",
"fV c #3483b5",
"fS c #3484b6",
"iZ c #356989",
"eY c #3585b5",
"eZ c #3586b7",
"#I c #3685b7",
"#H c #3686b7",
"iq c #387092",
"es c #387ca5",
"fG c #3883b2",
"eu c #3a87b6",
"fy c #3a87b7",
"fv c #3a87b8",
"fz c #3a88b8",
"ey c #3b708f",
"hW c #3b7293",
"ex c #3b89b8",
"et c #3b89b9",
"aA c #3c89b9",
".T c #3d708e",
"c3 c #3d7aa0",
".r c #3d85b2",
"j2 c #3e6980",
"hj c #3e7494",
"fj c #3e7596",
"#s c #3e7891",
"fg c #3e87b4",
".x c #3e89b7",
"gv c #3f7799",
"fa c #3f8bba",
"ic c #40728f",
"dT c #408ab7",
"fd c #408bb9",
".s c #408bba",
"#E c #417fa5",
"dO c #418dbb",
"gY c #427695",
"cZ c #4283ab",
".J c #437795",
"ac c #437b9b",
"c2 c #4387b1",
"eV c #438ab6",
".t c #45788b",
"gK c #457897",
"eS c #458ebb",
"ap c #467fa3",
"cX c #468eba",
"eP c #468fbc",
"#C c #478fbb",
"cY c #4790bd",
"gq c #487a98",
"#q c #488bb4",
"#D c #4891bd",
"gc c #497a98",
"#R c #497c9b",
"cl c #4982a5",
"dS c #4a7e9e",
"cS c #4a81a2",
".n c #4a84a7",
"ep c #4a8fb9",
".i c #4b84a6",
"el c #4b92bd",
"ar c #4b92be",
"g. c #4c7c99",
"a8 c #4c7f9d",
"em c #4c92be",
"#r c #4c93be",
"aq c #4c93bf",
"aI c #4d7388",
"fZ c #4d7c99",
"cn c #4d93be",
"cs c #4d94bf",
"ge c #4e7a95",
"cm c #4e94bf",
"fR c #4f7e9a",
"dP c #4f809c",
"fH c #507e9a",
"#G c #507f9d",
"bT c #5091b8",
"dG c #5094be",
"ct c #517c94",
"dN c #517e98",
".j c #51819e",
"dB c #5196c0",
"fu c #52809b",
"bK c #52829f",
"fh c #53809b",
".o c #53819b",
"bS c #5384a2",
"aJ c #5387a5",
"g4 c #547e97",
"am c #54829e",
"aT c #548aa9",
"cP c #5494bc",
"bJ c #5498c1",
"cQ c #558099",
"aZ c #5592b6",
"cO c #5596bd",
"as c #567d93",
"f# c #56829c",
"a7 c #5694b9",
"cV c #5698bf",
"fn c #577e94",
"eW c #57829c",
"aK c #578baa",
"cg c #5793b8",
"aX c #5795bb",
"cU c #5798c0",
"cT c #5799c1",
"cN c #579ac2",
".y c #58849d",
"dH c #5889a6",
"aU c #588ead",
"ch c #5896bb",
"jK c #598299",
"jO c #59829a",
"eO c #59849d",
"eq c #5a849e",
"d3 c #5a850c",
"iM c #5a8609",
"ce c #5a869f",
"aY c #5a9cc3",
"ix c #5b8199",
"d2 c #5b8411",
"ei c #5c869e",
"cJ c #5c890b",
"cd c #5d9dc4",
"gg c #5e8398",
"ii c #5e8d09",
"dZ c #5e8e08",
"eM c #5e9104",
"dA c #6088a0",
"da c #608f0b",
"iI c #609106",
"f0 c #61869b",
"ia c #61879b",
"fA c #61889f",
"b0 c #618f10",
"f9 c #61910a",
"dc c #619209",
"hy c #619404",
"gF c #619406",
"ef c #619503",
"jP c #62859b",
"ci c #62889e",
"ca c #628c16",
"cF c #628c17",
"ah c #628ea2",
"fO c #62920c",
"hG c #62930a",
"gi c #629603",
"eC c #629703",
"dh c #629704",
"dL c #6389a0",
"cM c #638aa1",
"go c #638f12",
"gI c #639013",
"iL c #639508",
"dY c #639803",
"#O c #639903",
"#P c #639a02",
"dm c #648b1d",
"b5 c #648f17",
"b2 c #64930f",
"bX c #649a05",
"ja c #65889d",
"iU c #659017",
"cG c #659d02",
"bI c #668a9e",
"cc c #668ca2",
"fQ c #669412",
"in c #669414",
"ft c #669908",
"dt c #66990b",
"iR c #669e02",
"d5 c #67901b",
"dz c #679318",
"#M c #679f02",
"c. c #67a002",
"#4 c #688c2b",
"e7 c #68911e",
"eG c #68911f",
"eg c #689515",
".W c #689a31",
"ik c #68a002",
"iW c #68a003",
"ds c #68a101",
"d6 c #68a102",
"dg c #68a103",
"dp c #699617",
"hR c #69a201",
"ec c #69a301",
"iV c #69a302",
"gP c #6a93ac",
"#2 c #6a9421",
"#3 c #6a9422",
"f8 c #6aa303",
"iO c #6aa502",
"hf c #6b9224",
"hV c #6b9321",
"f6 c #6b981a",
"f5 c #6ba405",
"cw c #6ba501",
"hH c #6ba502",
"#x c #6ba602",
"#L c #6ba702",
".m c #6c8c9f",
"#1 c #6c902b",
"iP c #6c9126",
"e. c #6c9325",
"f7 c #6c991b",
"ih c #6ca701",
"d9 c #6ca702",
"dl c #6ca802",
"aV c #6d8693",
"hL c #6d9325",
"ho c #6d95ad",
"b6 c #6da901",
"cy c #6da902",
"#m c #6e926f",
"cx c #6eaa02",
"bW c #6eab02",
"cC c #6f932d",
"io c #6fab01",
"c# c #6fac01",
"cK c #6fac02",
"cz c #6fad02",
"gX c #70952e",
"g3 c #7097ae",
"hU c #70ad02",
"fP c #70ae01",
"b1 c #70ae02",
"#V c #7191a3",
"ab c #7193a6",
"ed c #71952d",
"eK c #71952e",
"cA c #719530",
"#N c #71af02",
"dU c #7291a1",
"ag c #7396a3",
"#d c #73a231",
"aS c #748f9e",
".H c #749870",
"aL c #7592a2",
"cr c #7693a4",
"gw c #7695a8",
"gx c #7696a8",
"hC c #769a35",
"iJ c #77983b",
"h. c #7896a5",
"fe c #7898aa",
"if c #78993b",
"hN c #799445",
"ew c #7996a7",
"hT c #799c3a",
".0 c #7ab315",
".h c #7b95a4",
"eX c #7b97a6",
"co c #7b98a7",
"#6 c #7b9aa9",
"#n c #7b9aad",
".Q c #7b9bad",
"#h c #7c8e5b",
"c7 c #7c964c",
"#B c #7c98a6",
"b7 c #7c9948",
"iX c #7e9a4b",
"fs c #7fa33e",
"e# c #809d4a",
"aN c #809eaf",
"h5 c #80a2b4",
"fr c #80a33e",
"fq c #80a33f",
"dC c #81929b",
"cf c #819daa",
"bx c #819eac",
"al c #819eae",
"#J c #819faf",
"h6 c #81a2b4",
"cL c #829d4f",
"en c #829ead",
"e8 c #829f4c",
"eJ c #829f4d",
".w c #82a17b",
"eT c #82a1b2",
"h4 c #82a5b7",
"gp c #839f4e",
"h1 c #83a5b7",
"f3 c #849daa",
"hu c #849dab",
"ai c #85a1a8",
"i2 c #85a1af",
"h3 c #86aabe",
"c8 c #879767",
"hS c #87a058",
"h2 c #87aabe",
"iQ c #88a257",
"hM c #89a356",
"gJ c #89a357",
"az c #89a3b1",
"ad c #89a6b6",
"gj c #89aa4d",
"by c #8a9ea7",
"ev c #8aa3b0",
"hI c #8ba160",
"iG c #8ba35e",
"dV c #8ba45d",
"gW c #8baa50",
"dy c #8ca165",
"eA c #8ca45d",
"fp c #8ca65e",
"bE c #8caab9",
"ha c #8cab51",
"bU c #8da5b1",
"bD c #8daab9",
"gy c #8ea0ab",
"#U c #8ea7b5",
"bC c #8eaab8",
"bF c #8eaab9",
"cW c #90a4ae",
"iK c #90a668",
"hB c #90ac5a",
".9 c #90c139",
"f4 c #91a960",
"b# c #92a867",
"bw c #93a4ad",
"i1 c #93a6b1",
"is c #93a8b3",
"ba c #93a967",
"#c c #93abb5",
"hY c #94a9b4",
"bk c #94aa68",
"#l c #94bf49",
"e1 c #95a5ad",
"be c #95a674",
"#p c #95a9b3",
"hk c #95a9b4",
"bf c #95aa6a",
"g0 c #96aab4",
"iF c #96abb5",
"d# c #97a47d",
"gM c #97abb5",
"#w c #98a879",
"bj c #98a978",
"ip c #98ab74",
"gs c #98abb5",
"bb c #98ad71",
"gz c #99aab3",
"ga c #99acb6",
"fT c #9aadb6",
"gk c #9baa7e",
"hl c #9baeb8",
"bs c #9bb36f",
"fF c #9cacaf",
"fw c #9cadb6",
"g1 c #9caeb9",
"gN c #9cafb9",
"bq c #9cb36f",
"br c #9cb370",
"fb c #9daeb6",
"gt c #9db0b9",
"bt c #9db470",
"an c #9db6c3",
"eQ c #9eaeb7",
"gb c #9eb0b9",
"hz c #9eb276",
"ej c #9fafb7",
"fU c #9fb0ba",
"fx c #9fb1ba",
"bp c #9fb376",
"#u c #a0aa8c",
"df c #a0ae84",
"hJ c #a0b080",
"fc c #a0b1ba",
"#z c #a1ae88",
"eR c #a1b2ba",
"b9 c #a1b47b",
"hF c #a1b57a",
"i6 c #a2b1b8",
"hp c #a2b1b9",
"ek c #a2b2ba",
"hO c #a2b580",
"#Z c #a2b8c3",
"iw c #a3b1b9",
"bg c #a3b286",
"hD c #a3b77d",
"aW c #a4b3b9",
"hE c #a4b87e",
"iH c #a5b386",
"dW c #a5b485",
"e4 c #a5b9c1",
"#A c #a6af94",
"ea c #a6b48a",
"e9 c #a6b48b",
"j0 c #a6bbc4",
"#v c #a8b590",
"dk c #a9ad9e",
"dF c #a9b9c0",
"bM c #a9bac1",
"dq c #aab78f",
".8 c #aad065",
"bu c #abb990",
"j# c #abbfc7",
"i7 c #acb8bf",
"#y c #acbb8d",
"aQ c #acc0ca",
"#e c #acd16b",
"ig c #aeba96",
"a0 c #aebdc3",
".F c #aed373",
"a6 c #afbabf",
"hb c #b0b99e",
"bl c #b0bc95",
"bG c #b0bfc4",
"ht c #b0c2ca",
"gG c #b1b99f",
".G c #b1d471",
"dd c #b2b7a7",
"fI c #b2bfc5",
"gD c #b3c0c5",
"#b c #b4c0c5",
"jV c #b4c3c9",
".B c #b6c1c6",
"hA c #b6c2a1",
"bB c #b6c3c8",
"a. c #b6cad2",
"cv c #b7bfa7",
"bV c #b7c0a6",
"jF c #b7c3ca",
"jE c #b7c4ca",
"du c #b8bfa8",
"c1 c #b8c1c6",
"de c #babfb1",
"eo c #bac5c6",
"dI c #bbc2c5",
"#o c #bbc6cb",
"bY c #bcc8a6",
".u c #bcdb85",
".q c #bdc5c9",
"iC c #bec8cc",
"eU c #bec9c9",
"ff c #bec9ca",
"jD c #bec9ce",
".k c #becbd0",
"aC c #becfd6",
"bQ c #bed1d8",
".v c #bedc83",
"c4 c #bfced4",
"do c #c0c4b7",
"#K c #c0c7b1",
".1 c #c0dd94",
"c0 c #c1ccd0",
"g7 c #c1cfd2",
"iT c #c2cab0",
"jq c #c3cab5",
"jt c #c3cab6",
".2 c #c3d3da",
"jh c #c4c9b7",
"bo c #c4cab4",
"jf c #c4cbb5",
"er c #c5ced1",
"#t c #c5d4d5",
"dK c #c6cbcc",
"dD c #c7cacb",
"fC c #c7cfd0",
"eb c #c8cfba",
"he c #c8cfbb",
"fB c #c8cfd0",
"af c #c8d0cc",
"a1 c #c8d0d3",
"it c #c8d1d4",
"dn c #c9cbc3",
"c9 c #c9cbc5",
"#F c #c9d4d8",
"d. c #cacbc5",
"d8 c #caccc4",
"dJ c #caced0",
"fD c #cad2d4",
".6 c #cad7dc",
".p c #cbd7da",
".3 c #cbdde4",
"jW c #cccfd0",
"hQ c #ccd1c0",
"jr c #ccd1c2",
"dr c #ccd3bd",
"hx c #ccd5d8",
"b3 c #ced5c1",
"#Q c #ced8b9",
".M c #cee2b1",
"jw c #cfd3c4",
"cH c #cfd6c1",
"dE c #d0d2d3",
"ji c #d0d4c8",
"fE c #d0d9db",
"dx c #d1d3cb",
"bc c #d1d8c2",
"hd c #d2d4ca",
"eH c #d2d4cb",
"jG c #d2d6d7",
"jn c #d2d7c5",
"d7 c #d3d5cc",
"c6 c #d3d6cd",
"jm c #d3d9c5",
"dw c #d4d6cd",
"dv c #d4d6ce",
"jo c #d4d8c9",
"h7 c #d4d9dc",
"a9 c #d4e0e4",
"il c #d5d7d0",
"iS c #d5d7d1",
"jk c #d5dbc6",
"ck c #d5dbdc",
"jl c #d5dcc5",
"jx c #d6d9cc",
"cR c #d6e0e4",
"js c #d7dacf",
"ao c #d7dadb",
"b. c #d7dbcd",
"fo c #d7ddca",
"je c #d8dbd2",
"fM c #d8e4e8",
"dj c #d9dcd3",
"jz c #dae4e5",
"fN c #dbe2cb",
"jA c #dbe4e5",
"cb c #dce1cf",
"gQ c #dde0e1",
"hh c #dde1d1",
"jd c #e0e8e9",
"dX c #e1e3db",
"eE c #e2e4db",
"ee c #e2e7d8",
".7 c #e2edef",
"eB c #e3e5dd",
"eF c #e3e5de",
".Z c #e3efc9",
"bh c #e4e6df",
"di c #e4e7df",
"jy c #e4eaeb",
"gh c #e5e7df",
"jj c #e5e7e0",
"h8 c #e5e7e8",
"jS c #e5eef0",
"bR c #e6e9e9",
"aH c #e7e9e9",
".e c #e7ebec",
"eL c #e7ecdc",
"iB c #e7f0f2",
"jL c #e8ebec",
"aj c #e8f0ea",
"ez c #e8f0f2",
"a5 c #e8f2f5",
"bL c #e9eeee",
"jC c #e9eeef",
"ie c #ebede3",
"gE c #ebede4",
".b c #eceded",
"dR c #eceeee",
"hP c #edeeeb",
".S c #edf0f1",
"fi c #edf1f1",
"#0 c #eef0e8",
"bv c #eef3e5",
"cq c #eef8fb",
"aa c #eff3f4",
".X c #eff7e0",
"cj c #f0f4f5",
"jp c #f1f1ef",
"jB c #f1f4f4",
"cI c #f1f6e6",
"c5 c #f2f3f0",
"aE c #f2f4f3",
"ju c #f3f4f3",
".l c #f3f4f4",
"d0 c #f3f5ec",
"eD c #f3f5ed",
"h# c #f3f5ee",
"iY c #f3f5ef",
"dQ c #f3f6f6",
"cu c #f3f9fa",
"im c #f4f5ed",
"jv c #f4f5f0",
"av c #f4f6f6",
"#g c #f5f5f3",
"db c #f5f7ee",
"gn c #f5f7f0",
"ak c #f5f9fa",
"bH c #f5fafb",
".c c #f6f8f7",
"dM c #f6f8f8",
"ij c #f7f7f3",
"iN c #f7f8f3",
"aF c #f7f9f8",
".f c #f7fafa",
"gH c #f8f9f6",
"bZ c #f8faf1",
"d1 c #f8faf2",
"bm c #f8faf3",
"#. c #f8fbee",
"#5 c #f8fbef",
".5 c #f8fcfd",
"j4 c #f8fdfd",
"j5 c #f8fefe",
"hc c #f9f9f5",
"aw c #f9fafa",
"ae c #f9fcfd",
"jg c #fafaf8",
"aD c #fafaf9",
"aG c #fafbfa",
"gd c #fafbfb",
"#i c #fafcf5",
"gm c #fafcf8",
"ax c #fafcfb",
"id c #fafcfc",
"j3 c #fafcfd",
"b4 c #fafdf4",
"cp c #fafefe",
"gl c #fbfcf7",
"bd c #fbfcf8",
"hK c #fbfcfa",
".g c #fbfcfb",
"#a c #fbfcfc",
"cE c #fbfdf4",
"#k c #fbfdf6",
"bA c #fbfdfd",
".K c #fbfefe",
"d4 c #fcfcf7",
"au c #fcfcfc",
"b8 c #fcfdf9",
"cD c #fcfdfb",
"aR c #fcfdfc",
"aM c #fcfdfd",
"bi c #fcfef9",
".z c #fcfefe",
"e6 c #fdfdf8",
"hg c #fdfdfb",
".4 c #fdfdfc",
".d c #fdfdfd",
"bz c #fdfdfe",
"cB c #fdfefa",
"bn c #fdfefb",
"#j c #fdfefc",
"ay c #fdfefd",
".R c #fdfefe",
"hi c #fefefb",
"#f c #fefefc",
".L c #fefefd",
".a c #fefefe",
"a# c #fefeff",
"eh c #fefffc",
"e5 c #fefffd",
".# c #fefffe",
".Y c #feffff",
"eI c #fffefc",
"## c #fffefe",
"at c #fffeff",
"eN c #fffffc",
"f. c #fffffd",
".A c #fffffe",
"Qt c #ffffff",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.#.#.#.a.b.c.a.#.#.a.d.e.f.a.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a.a.g.h.i.j.k.a.a.l.m.n.o.p.a.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a.a.q.r.s.s.t.u.v.w.x.s.s.y.z.aQt.A.AQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a.a.B.C.D.D.E.F.G.H.I.D.D.J.K.aQt.A.AQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a.L.M.N.O.P.Q.R.a.S.T.U.V.W.X.#.AQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.A.Y.A.a.Z.0.1.2.3.z.a.4.a.5.6.7.8.9#..a.A##QtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a#a#b#c#d#e#f.a.L.a#g#h#i.L#j.a#k#l#m#n#o.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a#p#q#r#s#t.a.a#u#v#w#x#y#z#A.L.a#B#C#D#E#FQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a#G#H#H#I#J.a.a#K#L#M#N#O#P#Q.a.R#R#S#S#T#UQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a#V#W#X#Y#Z.a.a#0#1#2#3#3#4#5.a.a#6#7#8#9a.QtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQta#aaabacadae.a.a.aafagahaiaj.L.a.aakalaman.zQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.A.a.a.R.aa#.a.Laoapaqaqaras.5.a.a.a.a.a.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtat.aauavawaxay.aazaAaAaAaAaBaC.aaDaEaFaG.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a.aaHaIaJaKaLaMaNaOaOaOaOaPaQaRaSaTaUaV.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtat##.#Qt.YQtQtQtQtQtQt.a.a####.aQtQt##Qt.YQt.Y.###.Y.a.a.#.A.A.#.aQt.YQtQtQtQtQtQtQtQt.A.Aat.#.Y.#.aa#.A.a.AQtQtQt.Y.Yat.a.Yat.A.a.Y.AQtatQtQtQta#at.a.a.aa#atatQta#.Y.a.a.aaWaXaYaZa0a1a2a3a3a3a4a5a6a7aYa8a9.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtb.b#bababababababababababbbc.L.aQt.Ybdbebababababababfbgbh.a.#bibjbababababababababababkblbm.a.a.#.abnbobpbqbrbrbqbqbsbtbubv.a.a.abwbxbxbxbxbxbxbybz.abAbBbCbDbDbEbEbEbFbGbHaxbIbJbJbKbLbMbNbObPbQbRbSbJbTbU.a.a.AQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtbVbW#N#N#N#N#N#N#N#N#N#N#NbXbY.aQt.YbZb0#N#N#N#N#N#N#Nb1b2b3.ab4b5#N#N#N#N#N#N#N#N#N#N#Nb6b7b8.a.L#fb9c.#N#N#N#N#N#N#N#Nc#cacb.a.acccdcdcdcdcdcdceaM.zcfcgcdcdcdcdcdcdcdchcicjckclcmcnco.Rcpcqcp.acrcscmctcu##.a.AQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtcvcwbW#N#Ncxcycycycycycz#N#NcAcB.#a#bZb0#N#N#N#N#N#N#N#N#NcCcDcEcFcyb1#Nczcycycycycycx#N#NcGcH.a.acIcJ#N#NcKcycycycycyb1#Nb1cL.L.acMcNcNcOcPcPcPcQbAcRcScNcNcTcUcUcUcUcNcNcV#p.acWcXcYcZc0.a.a.ac1c2cYc3c4.a.#a#.YQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtc5c6c7#N#Nc8c9c9c9d.c9d#cx#Ndadb.aa#bZb0#Ndcdddedededfdg#Ndhdi.Ldjdkdl#Ndmdnd.d.d.c9dodp#Nb1dq.a##drds#NdtdudvdwdvdvdxdycK#Ndz#f.#dAdBdBdCdDdDdDdE.adFdGdBdHdIdJdJdJdK#VdBdBdL.adMdNdOdOdPdQ.adRdSdOdTdU.R.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a.adV#N#NdW.AQtQt.a.#dXdY#NdZd0.aatd1d2#Md3c5.a.a.ad4d5#Nd6d7.a.ad8d9#Ne.#f.aQtQt.a.ae##N#Nea.a.Aebec#Ned.L.a.A.A.a.aeeef#Negeh.Yeiararejatat.a.a.aekelemen.a.aQt.a.aeoepemeq.a.aereseteuev.aewexeteyez.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.A.aeA#N#NdW.A.A.Aa#.aeBeC#NdZeD.A.a.LbheEeF.4.a.a.acBeG#Nd6eH.a.ad8d9#Ne.eIQt.A.A.#.aeJ#N#Nea.#.aebec#NeK.L.YQtQt.a.aeLeM#NegeN.#eOePePeQa#at##a#.aeReSePeT.#.a.a.a.aeUeVePeW.#.a.aeXeYeZe0e1e2eZe3e4.a.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.AdV#N#NdW.AQtQtQtQteFeC#NdZeDQt.#.a.a.L.L#f#fe5e5e6e7#Nd6eHQtQtd8d9#Ne.eNQtQtQtQt.Ae8#N#Ne9.AQtebec#NeKf.QtQtQtQtQteLeM#NegeN.Yf#fafafbQtQtQtQtQtfcfd.sfe.#.a.YQt.afffg.sfh.YQt.afifjfkfkflfkfmfncp.aatQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.AdV#N#NdW.AQtQtQtQteFeC#NdZeDQt.a.Lfofpfqfrfqfqfqfsft#Nd6eHQtQtd8d9#Ne.eNQtQtQtQt.Ae8#N#Ne9.AQtebec#NeKf.QtQtQtQtQteLeM#NegeN.YfufvfvfwQtQtQtQtQtfxfyfzfAfBfCfDfEfEfFfGfzfH.YQt.a.afIfJfKfKfKfLfM.a.YQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.AdV#N#NdW.AQtQtQtQteFeC#NdZeDQt.afNfOfP#N#N#N#N#N#N#N#Nd6eHQtQtd8d9#Ne.eNQtQtQtQt.Ae8#N#Ne9.AQtebec#NeKf.QtQtQtQtQteLeM#NfQeN.YfRfSfSfTQtQtQtQtQtfUfVfSfWfXfXfXfYfYfXfSfSfZ.#.#.a.aayf0f1f1f2f3.a.a.YQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.AdV#N#NdW.AQtQtQtQteFeC#NdZeDQt.Lf4#N#Nf5f6f7f7f7f6f8#Nd6eHQtQtd8d9#Ne.eNQtQtQtQt.Ae8#N#Ne9.AQtebec#NeKf.QtQtQtQtQteLeM#Nf9eN.Yg.g#g#gaQtQtQtQtQtgbg#g#g#g#g#g#g#g#g#g#g#gc.a.a.#.agdgegfgf#Xgg.R.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.AdV#N#NdW.AQtQtQtQtghgi#NdZeDQte5gj#N#Ngkglbdbdgmgngo#Nd6eHQtQtd8d9#Ne.eNQtQtQtQt.Agp#N#Ne9.AQtebec#NeKf.QtQtQtQtQteLeM#Nf9eN.YgqgrgrgsQtQtQtQtQtgtgrgugvgwgxgxgxgxgxgxgxgy.a.a.a.agzgAgBgBgBgCgD.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.AdV#N#NdW.AQtQtQtQtgEgF#NdZeD.ae5gj#N#NgG.a.a.#.agHgI#Nd6eH.a.Ad8d9#Ne.eNQtQtQtQt.AgJ#N#Nea.A.aebec#NeKf.QtQtQt.AQteLeM#Nf9eN.YgKgLgLgMQtQtQtQt.YgNgLgOgP.a.a.YQtQt.a.a.a.a.a##.agQgRgSgTgUgSgSgVaa.a.AQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.AdV#N#NdW.AQtQtQtQtgEgF#NdZd0.Y.LgW#N#NgG.a.a.a.#gHgI#Nd6eH.a.#d8d9#Ne.eNQtQtQtQt.AgJ#N#Ne9.a.aebec#NgX.LQt.AQt.a.AeLeM#Nf9eN.#gYgZgZg0QtQtQtQt.Yg1g2g2g3.aa#a#QtQt.a.a.a.a.a.aaug4g5g5g6g7g8g5g9h..a.a##QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.AdV#N#NdW.AQtQtQtQtgEgF#NdZh#.a.Lha#N#Nhb.a.a.#.ahcgI#Nd6hd.L.ad8d9#Ne.eNQtQtQtQt.AgJ#N#Ne9.a.aheec#Nhfhg.a.AQt.A.ahheC#Nf9hi.#hjg5g5hkQtQtQt.a.ahlhmhnho.aa#.YQtQt##.a.a.a.a.ahphqhrhsht.ahuhvhrhwhx.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQt##.#dV#N#NdW.AQtQtQt.AgEgF#NhyhzhA.LhB#N#NhChDhEhEhEhFhG#NhHhIhJhKd8d9#NhLeNatQtQtQt.AhM#N#NhNhOhPhQhR#NhHhShEhEhEhEhDhThU#NhVeh.#hWhXhXhYQt.YQt.a.agNhZhZh0h1h2h3h2h4h5h5h6h7.ah8h9i.i#ia.z.adQibi.i.icid.a.#.#QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a.adV#N#NdW.AQtQt.A.AiegF#N#N#Nif.Ligih#N#N#N#N#N#N#N#N#N#N#Niiijd8d9#Ne.#f.a.aQt.###gJ#N#N#Nikilimin#N#N#N#N#N#N#N#N#N#Nioip.L.#iqiririsa#a#Qt.a.aitiuiviviviviviviviviviviw.dixiyiziAiB.a.a.aiCiDiziEiF.a.#.aatQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a.LiGcKcKiH.aQtQt.A.agEiIcKcKcKiJ.LbdiKiLcycycycycyd9hHhHhHhHiMiNd8iOcKiPhi.#QtQt.a.aiQcKcKcKiRiS.aiTiUiVcKcKcKcKcKcKcKiWiXiY.a.aiZi0i0i1a#atQtQt.a.ai2i3i4i5i5i5i5i5i5i5i5i6i7i8i9j.j#.a##.a.a.ajajbi9jcjd.a.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a.ajejfjfeF.aQt.A.A.ajgjhjfjfjfji.a.a.Ljjjkjljljljljmjnjnjnjnjo.4jpjqjfjr.L.#QtQt.a.ajsjfjfjfjtju.a.ajvjwjfjfjfjfjfjfjfjxhg.a.a.ajyjzjAjB.aQtQtQt.a.a.ajCjDjEjEjEjEjEjEjFjFjGjHjIjJjK.K.aata#.a.ajLjMjIjNjO.z.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.aQtQt.aQtQtQtQtQt.a.aQtQt.a.aQtQt.a.aQtQtQtQtQtQtQtQtQtQtQtQt.a.aQtQt.aQtQtQtQt.a.a.a.a.a.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQt.a.a.a.aQtQtQtQtQtQtQtQt.a.a.aQtQtQtQtQt.a.a.ajPjQjQjRjS.a.aQtQt.a.a.aeRjTjQjUjV.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt.A.ajWjXjYjZj0.a.a.aQtQt.#.a.aaRctj1jYj2j3.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt##.aayj4j4j5.R.a.a.aQtQt.#.a.L.a.zj4j4j4.a.aQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt"
]
image3_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x03" \
    "\x01\x49\x44\x41\x54\x38\x8d\x9d\xd3\x5d\x88\x94" \
    "\x65\x14\xc0\xf1\xff\xf3\xf5\xce\xb3\x33\xeb\x8c" \
    "\xc9\xe4\xae\x88\xad\x29\xa5\x2d\xbb\x21\x06\x6d" \
    "\x42\xb5\x64\x48\x10\x0b\x45\x97\xc2\x5e\x77\x15" \
    "\x45\x44\x20\x28\x94\x50\xdd\x46\x41\x17\x86\x7d" \
    "\x50\x1b\x65\x26\x45\x1f\x5a\xe8\x45\xb5\xa9\x5d" \
    "\x04\x11\xb1\x6a\x94\xb2\xe9\xae\xe3\xc8\xec\xec" \
    "\x7c\xef\xbc\xef\xbc\x73\xba\xd0\x8d\xb4\x75\x77" \
    "\x76\x1f\x78\x6e\x0e\xe7\xfc\x38\xe7\xf0\x3c\x4a" \
    "\x44\x58\xe9\x51\x2f\x2b\x4f\x17\x0e\x80\x9f\x48" \
    "\xd2\x44\xf3\x2d\x35\xa0\xa2\x57\x8c\xde\xa9\x86" \
    "\x4d\xce\xfc\x6e\x67\xed\xa4\x9d\xb5\x93\x76\xab" \
    "\x3d\x6f\x56\x99\xdf\x48\xf1\x3a\xd0\x6d\x57\x84" \
    "\x2a\x75\x9b\x7e\x58\xbf\xe1\xee\x72\x9b\x31\xd7" \
    "\x62\x72\x59\x08\xc7\xc3\x59\x6a\xbc\x2f\x22\x95" \
    "\x65\xc3\x4a\x29\xa5\xfb\xf4\x0b\xc1\x83\xc1\xa0" \
    "\xf6\xd7\x06\x96\xba\x10\x7d\x1d\x35\x25\x27\x7b" \
    "\x45\xe4\x7b\x80\xe5\x77\x6c\xd9\x61\xef\xb5\xcf" \
    "\xb8\x8d\x4e\xa1\x80\x36\x84\xa7\x42\xe2\x33\xf1" \
    "\xdb\xc0\xd8\x7c\xda\xb2\x76\xac\x94\x0a\xec\x26" \
    "\xbb\xcf\xef\xf4\xab\x4c\x60\x30\xce\xd0\x3e\xd7" \
    "\x26\x3c\x1e\x8e\x13\xf3\x8a\x88\x84\x2b\x82\x4d" \
    "\xda\xec\xf2\xc3\x7e\xa7\x5b\xeb\x30\xce\x20\x93" \
    "\xc2\xdc\x47\x73\x57\xa5\x2c\x2f\x8a\x48\xee\xbf" \
    "\xb9\x1d\xc3\x4a\xa9\xb4\x1d\xb4\xaf\xfa\x87\x7c" \
    "\xa0\x03\x0d\x75\xa8\x7f\x5a\x6f\xc5\xb9\x78\x3f" \
    "\x70\xfa\xe6\xfc\x8e\x61\xb3\xde\x3c\x95\x7a\x3c" \
    "\x35\x60\xd3\x16\xad\x34\x8d\xcf\x1b\x44\x13\xd1" \
    "\x11\xe0\x1d\x59\xe0\x33\x74\x04\x2b\xa5\x92\x7e" \
    "\x9b\x7f\xde\x0f\x7a\x6d\x02\x43\xf4\x4b\x44\xe3" \
    "\x44\xe3\x2c\x6d\xf6\x89\x48\x7d\xa1\x9a\x8e\x60" \
    "\xdf\xef\xef\xeb\x7e\xb4\xfb\x1e\xdb\x65\xa1\x04" \
    "\xd5\x43\x55\x91\x39\x39\x20\x22\x7f\xdc\xaa\xa6" \
    "\x23\xd8\xf5\xbb\x51\xdf\xef\xad\x76\x9a\xc6\x78" \
    "\x83\xf0\x7c\x38\x01\x1c\x5a\xac\xc6\x2a\xa7\x1e" \
    "\x4b\xdd\x9f\xda\xa6\x32\x2a\x31\x1f\x94\xaa\x44" \
    "\xb5\x93\xb5\x73\xc4\x7c\x45\x0f\xae\xf7\xd9\xde" \
    "\x11\x9b\xb6\x44\xd3\x11\xd5\x6f\xaa\x82\x70\x50" \
    "\x44\xa6\x16\x85\x11\xd6\xbb\x3b\xdc\xfe\xec\xd3" \
    "\xd9\x60\xfe\x7b\xc6\x85\x98\xe9\xcb\xd3\xd5\xe6" \
    "\x9f\xcd\x91\x35\x4f\xac\x59\x9b\xdc\x9e\xec\x31" \
    "\xce\x30\x73\x64\x86\xf0\x42\x78\x09\xf8\x72\xa9" \
    "\x29\x35\x31\x1f\x56\xbe\xab\xbc\x5b\xfb\xa1\x86" \
    "\xcb\x38\x5c\xc6\xe1\x37\x79\x56\x3f\xb9\xba\x1b" \
    "\xcd\x68\xf2\xee\xe4\xee\xc4\xba\x84\x6e\x5d\x6c" \
    "\x51\x39\x5e\x01\x38\x0c\xfc\xb5\x24\x2c\x22\x61" \
    "\x3c\x13\xbf\x54\x78\xaf\x70\x3a\x3c\x1b\x62\x02" \
    "\x83\x09\x0c\x99\x5d\x19\x12\x1b\x13\x23\x89\x0d" \
    "\x89\x47\x8c\x33\x94\xbe\x28\xd1\xca\xb7\xa6\x80" \
    "\x83\x0b\x3d\xaf\xff\x77\x0c\x88\x48\x2e\xbc\x10" \
    "\x3e\x97\x7f\x33\x7f\x25\xbe\x1a\x63\x02\x43\xd7" \
    "\xe6\x2e\xb2\xa3\xd9\x9e\xc4\x86\x44\x26\xfa\x3b" \
    "\xa2\x7c\xac\x0c\x70\x0c\x98\x58\x0a\xfd\x17\xbe" \
    "\x8e\xff\x5c\x19\xaf\xec\xc9\xbf\x95\x0f\x69\x82" \
    "\x0e\x34\xd9\xdd\x59\x82\x75\x01\xc5\xc3\x45\xa2" \
    "\x2b\x51\x19\xf8\xa0\x93\x6e\x6f\x80\xaf\x9f\xb1" \
    "\xe2\x67\xc5\x03\x85\xb1\x02\xda\x68\x5c\xc6\xd1" \
    "\x2e\xb6\x29\x9d\x28\x01\x1c\x05\x4e\x75\x82\xce" \
    "\x77\x7a\xc3\x05\x7a\xdd\xed\xee\xc7\x2d\x9f\x6c" \
    "\x91\xa1\x99\x21\xe9\x7b\xad\x4f\x50\x94\x80\xe1" \
    "\x9b\x73\x17\xbb\x0b\x07\x61\x28\xb9\x35\x39\x35" \
    "\x70\x74\x40\xd2\x3b\xd2\x02\x7c\x0c\x04\xcb\x81" \
    "\xd5\xad\x56\xa6\x94\x1a\x4e\x3f\x90\xde\x5e\xfb" \
    "\xb5\x56\x8e\xe7\xe2\x93\x22\x72\xa6\xe3\x35\x00" \
    "\xff\x00\x03\x11\x91\x02\xf5\x72\xea\x39\x00\x00" \
    "\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"
image4_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x03" \
    "\x15\x49\x44\x41\x54\x38\x8d\xb5\xd4\x5f\x68\x95" \
    "\x75\x1c\xc7\xf1\xf7\xf7\xf9\x3d\xe7\x39\xcf\x4e" \
    "\x4c\x0b\xc2\x46\x61\x8a\xb9\x10\xaf\xc2\x2e\x86" \
    "\xa8\xb0\x41\x37\x25\x48\x85\xd9\x45\x5e\xb4\x90" \
    "\x86\x4d\x02\xa1\x70\x14\x52\xbb\x10\x46\x66\xb4" \
    "\xfe\xc0\x06\x6b\x20\x2a\x4d\x27\x91\x15\x5e\x44" \
    "\xa5\x56\x28\xbb\x08\x02\x65\xe2\x22\x87\x0a\x9b" \
    "\x86\xb8\xa1\xb9\x7f\x3d\xe7\xf7\xe9\xe2\x9c\x33" \
    "\x9f\x73\x76\x0e\xcd\x8b\x7e\xf0\x85\xe7\x79\x7e" \
    "\xbf\xdf\xeb\xfb\x7b\xbe\xf0\xfd\x99\x24\xfe\x8f" \
    "\x11\xa4\x5f\x76\x45\x51\x53\x7b\x14\x7d\xb8\x2b" \
    "\x8e\x9f\x5c\xcc\xe6\x4e\xb3\xd0\xcc\xac\xda\x9c" \
    "\x95\x4e\xfc\x76\x14\x35\x79\xef\x8f\x60\xf6\x04" \
    "\xf0\xf1\xb5\x24\x79\xeb\x98\x94\xaf\x85\xee\x31" \
    "\xab\xcf\x87\xe1\x7b\x82\x39\x20\x8b\x73\xbd\x07" \
    "\x66\x66\x46\x4a\xf3\x61\xe9\xc1\x49\x9b\x32\x66" \
    "\xab\x00\x3c\xbc\xb6\x3a\x0c\xbf\x06\xce\xd4\x42" \
    "\x43\xe7\xba\x1c\xb4\x01\x0e\xf8\x21\x99\x9d\xbd" \
    "\x9d\x5e\x33\x5f\x8a\x81\x24\x99\xb8\x29\xf9\x18" \
    "\xc8\xc1\x92\x2c\xbc\xd3\x65\xf6\x50\x25\xfa\x81" \
    "\x59\x7d\xce\xb9\xae\xac\x59\x5b\x0c\xee\x96\x74" \
    "\xeb\xa0\xf7\x7f\xed\x87\xfa\xaa\xf0\x15\x48\x7e" \
    "\xf2\x5e\xff\x48\xc4\x85\x78\x26\x08\xc3\xf7\x3b" \
    "\xcd\xa2\x34\x8a\x73\x5d\x75\xd0\x16\x4b\x6e\xcc" \
    "\x7b\x06\xf3\xf9\xa5\x63\xde\x4f\x02\xd7\xab\xd6" \
    "\xd8\xcc\x96\x18\x9c\xd8\x68\xd6\xfc\x7c\x10\xe0" \
    "\x00\xc1\xb4\x49\x1d\x75\xde\xf7\x8d\x43\xf2\x60" \
    "\x18\xee\x47\x6a\x07\xdc\x4d\xe0\x90\xf7\xfe\x8a" \
    "\xd4\x03\x74\x48\xba\x53\x15\x2e\xe2\xcd\x59\x18" \
    "\x78\x31\x08\x1e\xd9\x64\x56\xfa\x9d\x39\xe0\x08" \
    "\xd2\x1f\x32\xdb\x6b\x50\x37\x05\xf4\x7b\xcf\x05" \
    "\xe9\x24\xb0\x5d\xd2\x44\x65\xc9\x2a\x61\x03\xda" \
    "\x63\x38\xf0\x92\x59\xd4\x72\x0f\x07\xc8\x03\x2e" \
    "\x01\x8e\x4a\xfc\x28\x8d\x78\xd8\x2a\xe9\x7c\x25" \
    "\x5a\x56\x63\x00\x15\xb2\xf4\xcf\x40\xdf\x71\x29" \
    "\xff\xab\x44\x06\xc8\x16\xc2\x65\x81\x3b\xc0\x88" \
    "\x74\xdb\xc3\xee\x5a\xe8\x02\xb8\x88\x4f\x01\x1d" \
    "\xd3\xf0\xf9\x6f\x30\x0b\x10\xa7\x62\x25\xd0\x19" \
    "\x04\x7f\x0f\x3a\x17\x0c\x9a\xb9\x5a\xb0\xd5\x6a" \
    "\xe9\x2f\xcc\x56\x67\x82\xe0\xe4\x32\x68\x84\x42" \
    "\xa1\x33\x40\xaa\xcd\x26\x0c\x0e\x26\xde\x7f\xba" \
    "\x59\xba\xbc\x28\xf8\x3b\xb3\xdc\x03\x41\xf0\x99" \
    "\x49\xad\x00\x53\x40\x8f\xc4\xa3\x66\x6c\x01\x72" \
    "\x69\x00\x86\xbd\xd4\x3d\x03\x03\xcf\x4a\xf3\x4d" \
    "\xb2\x10\x36\xb3\x73\xd0\x8e\xd9\x47\x06\x19\x0f" \
    "\x1c\x06\x7a\xa5\x49\x60\x69\x0b\xd8\xeb\x66\x3c" \
    "\x5e\xbe\x6b\x0e\x38\x8b\xd4\x93\x81\x6f\x9f\x96" \
    "\xa6\x16\xc0\xbf\x9b\x35\x7b\xb3\xa3\x01\x2c\x03" \
    "\x38\x0b\xbc\x2b\x5d\x9b\x84\x37\x80\x0d\xc0\xab" \
    "\x8d\xd0\xb0\xc3\x8c\x96\x62\x79\xca\x12\x48\xdb" \
    "\x9f\x92\x06\x91\x34\x1f\xc3\xb0\x62\xd8\x6c\xe8" \
    "\xa2\x99\x2e\x9a\xe9\x17\x33\xad\x83\x69\xa0\xb5" \
    "\x78\x00\x03\xd6\x03\xa7\x62\xf0\xdb\x40\xdf\x17" \
    "\xd7\x96\x62\x08\x76\x48\x62\x1e\x1d\x83\xdc\x28" \
    "\xf4\x8f\x82\x46\x41\x97\x41\x3b\x41\x01\xf4\x02" \
    "\x51\xfa\x00\x40\x03\xf0\x09\x70\xb7\x11\xb4\x0f" \
    "\xf4\x15\x68\x0f\x24\xeb\xa1\xad\x0c\xbe\x0e\x2f" \
    "\x8f\xc1\xdc\x38\x68\x1c\x74\x1a\xb4\x1c\x2e\x01" \
    "\xab\xd2\x68\x0a\x8f\x80\x56\xe0\xcf\x10\x94\x03" \
    "\x01\x9e\x42\x27\xde\x83\x4f\xc0\xe6\x2f\x61\xfc" \
    "\x06\xe8\x67\xd0\x0b\x85\x45\xbb\xab\xa1\x15\x09" \
    "\xd6\x02\x3d\xc0\x37\xc0\x2b\xc0\xc3\x65\x30\xf0" \
    "\x66\x0e\xfc\x73\xa0\x35\x85\xec\x17\x80\xc7\xfe" \
    "\x0b\x2e\xee\x0d\x81\xb8\xec\x5b\x6a\x72\x23\xd0" \
    "\x0d\x5c\x05\x4e\x01\xdb\x16\x83\xd6\x8a\x6a\x97" \
    "\xd0\x4a\x60\xb2\xda\x8d\x75\x3f\xe3\x5f\xbf\xdc" \
    "\x0a\xd6\x12\xa9\x67\xde\x00\x00\x00\x00\x49\x45" \
    "\x4e\x44\xae\x42\x60\x82"
image5_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x02" \
    "\x8d\x49\x44\x41\x54\x38\x8d\xbd\x95\x4f\x48\x14" \
    "\x51\x1c\xc7\xbf\x6f\xde\x7b\xb3\x3b\xbb\x9b\xda" \
    "\xa6\xe6\xb2\xfe\x09\x64\xc5\x02\xbb\x94\x15\x41" \
    "\x75\x13\xea\x60\x90\x7f\x0e\x9d\x12\x0f\x0b\x9d" \
    "\xb4\x82\x0e\x5d\x0a\xbc\xd4\xa1\x43\x41\x41\x97" \
    "\x8d\x0e\x45\x83\x74\xe9\x64\x54\x44\x5e\x0a\xc3" \
    "\x43\xa0\x60\x61\xb8\x66\x52\x89\xb2\x3b\xb3\xff" \
    "\x9c\x37\xb3\xd3\xc1\xd9\x75\xdc\xd5\xb0\xd6\xfa" \
    "\xc2\x0f\xe6\xf7\xde\xf0\x99\x2f\xdf\xf7\xde\x3c" \
    "\x62\xdb\x36\xfe\x85\xa4\xcd\x06\xc7\x87\x4e\x1e" \
    "\xfc\x31\x74\xf8\xe8\x8e\x82\x6f\x44\xbb\xdb\x5b" \
    "\x77\xdb\xb7\x9e\xcd\x2c\xbf\xab\x04\x4c\xdc\x51" \
    "\x5c\x89\x76\xd7\x9e\x0e\x26\xef\x9d\xd8\x63\xf7" \
    "\xcd\xc5\x75\x58\x19\x71\x73\xbf\x2d\xcd\x20\x63" \
    "\x00\x09\x01\x24\x72\x6b\xa5\x0b\xe8\x8b\x3a\x74" \
    "\x00\x3a\x80\x1c\x00\x0d\x10\x23\x2d\x2d\x8b\x63" \
    "\x73\x73\xaf\x01\x80\x15\xa0\xfd\xfd\xfd\xb4\xa7" \
    "\x2d\x79\xed\xd0\x5e\xa3\x4f\x36\x65\xb4\x85\x7c" \
    "\x40\xc2\xb8\x8a\xa4\x01\xd8\x04\xe0\x12\xc0\x29" \
    "\x20\x33\x80\x99\x60\x5c\x02\x13\xf9\x22\x80\x03" \
    "\x7a\x38\x1e\x8f\x96\x45\xd1\xd9\xf4\xf3\x5c\x47" \
    "\x68\x65\xa8\xa6\xda\x81\x00\x0e\x4c\x5a\xef\x65" \
    "\xba\xfe\x01\xc7\x15\x77\xbb\x73\x49\x02\x80\x48" \
    "\x24\x72\xec\xd5\xa4\xa6\xce\x27\x08\x2c\xc9\x04" \
    "\x58\x1e\x60\x5b\xc0\x9d\x31\xe6\xf4\xcc\x55\xd4" \
    "\x05\x66\x00\x10\x0e\x87\x23\x79\x2e\x67\xee\xbe" \
    "\x35\x7d\xf3\xed\xab\x38\xdf\x2e\x10\xe0\x1c\x36" \
    "\x97\xf0\x71\x29\x8b\x5c\x5a\x00\x29\x13\x24\x6b" \
    "\xc1\xc8\x98\x90\x57\xf3\xa0\x8c\x43\x81\x89\x1a" \
    "\x97\x73\x94\x82\xeb\xeb\xeb\x9f\xa6\xd3\x69\x46" \
    "\x88\x7c\xfd\xf9\xac\xd2\x9c\xb2\x08\xfa\x42\x1a" \
    "\x1a\x65\x69\xf5\xfe\xe7\xec\xc2\x87\x15\x34\x28" \
    "\x8a\x02\x0f\x93\x89\xc7\x0f\xe4\x15\x1b\x4a\x1d" \
    "\x27\x97\x67\x67\x95\xda\xe5\x44\x11\x56\xe6\x58" \
    "\x55\x55\x03\x40\xac\xb7\xb7\x77\x5a\x08\x71\xfb" \
    "\xe5\x17\x71\x3c\x8d\x46\x5c\x68\x58\x4a\x9d\x3d" \
    "\x50\x37\x31\xf6\x66\xe9\x85\xcf\x22\xf0\x7b\x65" \
    "\xf8\x7c\x3e\xf8\xfd\x7e\x54\x71\xda\x91\x9b\x9e" \
    "\x1a\xde\x2a\xe7\x0d\xfd\xe8\xe8\xe8\xfb\x81\x81" \
    "\x81\x1e\x4d\xd3\x46\x26\xe6\x53\x83\x59\xda\x5a" \
    "\x13\xaa\xd2\x52\x9d\x9d\xfb\x1e\xa9\xaa\x6a\xb9" \
    "\xdf\x3d\xd3\xd5\x75\xca\x10\x62\xb8\x00\x2d\xcd" \
    "\xb8\xec\x80\xc4\x62\xb1\xef\x94\xd2\x8b\xc1\x60" \
    "\x30\x3a\x3e\x39\xf5\x78\xc1\xdb\x74\xa9\x14\x5a" \
    "\x74\xc5\x36\x2e\x60\x59\x14\xa5\x72\xa2\x79\xe0" \
    "\xd4\xd6\xa2\x64\x6d\x77\x88\x7c\xd9\xd4\xa6\xff" \
    "\x8a\xed\xc8\xa6\x34\x03\x46\xd7\x0e\x0a\xca\x77" \
    "\xc5\x5f\x83\x0b\xe2\x9c\x16\x17\xef\xb7\x19\xff" \
    "\x91\x18\x59\x7f\xc4\x36\x32\xde\xb6\x3c\x0c\xa0" \
    "\x12\xbc\xc2\x82\xc8\x98\x1b\xa6\x2a\x8e\x02\x5c" \
    "\x2a\xc6\xe1\x86\x55\xe4\x38\x2e\x7b\x3f\x3d\xb4" \
    "\x6c\x85\x06\x3c\x30\x03\xdc\x5a\x6e\x6e\x39\x02" \
    "\xe0\x49\xc5\xe0\x3b\x39\xb2\x18\xd8\x55\xdd\x40" \
    "\x14\x42\x18\xe7\x46\xf2\xdb\x57\xa3\x30\x47\xfe" \
    "\xeb\x9d\xb7\x13\xfa\x05\x94\x85\xda\xeb\x0f\xa1" \
    "\xa8\xc1\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42" \
    "\x60\x82"
image6_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x02" \
    "\xcf\x49\x44\x41\x54\x38\x8d\xed\x94\x4d\x68\x13" \
    "\x51\x10\xc7\xe7\xbd\x7d\xd9\xec\x26\xeb\x26\x6d" \
    "\x92\x4d\x25\xa5\xb5\x55\x14\x2b\xf6\x54\xb4\x45" \
    "\xbc\x68\x05\xa9\x1f\x07\xc5\x83\x20\xa2\x20\xa5" \
    "\x07\x45\x0f\x1e\x44\x54\xd0\x83\x52\x4f\x82\x9e" \
    "\xc4\x0f\x54\x5a\x44\x2a\xa2\x22\x0a\x85\x88\x8a" \
    "\x1f\x68\x6c\x6b\xd1\xaa\x68\x1b\x5b\x35\x31\xb5" \
    "\x36\x5d\x9b\xd8\xdd\xcd\xdb\x37\x9e\x52\xab\xf6" \
    "\xda\x83\xe0\x9c\xe6\xf0\x9f\x1f\x33\xf0\x9f\x3f" \
    "\x41\x44\x98\x89\xa2\x33\x42\xfd\x0f\xfe\xb7\xc1" \
    "\xac\xd8\x6c\xdf\x7e\x58\x09\xea\x64\xbf\x99\x1d" \
    "\x6b\xe8\x7f\x9f\x2c\x7b\xd1\xfd\xb2\xd7\x2e\x90" \
    "\x4e\xcb\xd5\xdb\x10\x13\x85\xa9\x43\xfb\xf6\x9d" \
    "\xae\xd0\x54\x7a\x24\xd9\x3f\x58\x73\x37\xfe\x08" \
    "\x32\x5f\x46\x13\x0e\x61\xd7\x0a\x85\x67\x9d\x45" \
    "\x0d\x41\x44\x68\x6c\xdc\x13\x35\x42\x70\x6d\x5e" \
    "\x55\xb4\x6a\x51\x59\x30\x13\x09\x07\xa5\xec\xc8" \
    "\xc8\xc4\x95\xdb\x0f\xd4\xf8\xc3\x44\xdf\x48\xde" \
    "\x6d\x41\x1c\xcc\x02\x00\xac\x5b\xb7\x73\xe5\xfc" \
    "\xea\xc8\x89\x9a\xaa\x98\x1a\x55\xa9\xe9\xf1\xc8" \
    "\xac\xa7\xe7\x0d\xbf\x70\x33\x1e\x18\x18\x4a\xdf" \
    "\xb0\xc5\x87\xbd\x88\x28\x18\x00\x80\x65\x7d\x3d" \
    "\xee\x73\xf5\xc0\xfa\x85\x91\x97\xaa\x4f\x25\x00" \
    "\x02\xa2\xb1\x52\x38\xb0\x6d\xad\x69\x04\xfc\x95" \
    "\x67\xaf\xde\x39\x02\x00\xbb\x9a\x9a\xb6\xe8\x32" \
    "\xa1\x47\x17\xe9\x86\xb9\x34\xa6\x66\x8a\xdb\x95" \
    "\x2f\x5f\x08\x75\xf3\x42\xa3\x2d\xad\xe7\x57\x27" \
    "\x53\xe5\x09\x00\x68\x67\x73\x6a\x36\xce\x2e\x95" \
    "\xed\xfa\x5a\xb4\x13\xe9\x87\xf7\x27\xac\xef\x63" \
    "\xce\x8f\xcc\xb0\xad\x06\x82\x1e\x35\x1c\xf2\xd6" \
    "\x32\x57\x53\x55\xba\x86\x90\xc8\xa9\x05\xd5\x95" \
    "\x2b\x4a\x34\xc5\x08\xc7\x20\xfe\xee\x56\x1f\xcf" \
    "\x0f\x0f\xdb\xdc\xca\x73\x9f\x11\x55\x14\x3d\x28" \
    "\xaf\xac\x28\xb5\xce\xa5\x3f\xed\x00\x80\x76\x96" \
    "\x4e\xa6\x9a\x1d\xef\x84\xfc\xe3\xf3\xdb\xfe\x57" \
    "\xdc\x11\xc0\xc5\xaf\x1f\x67\x94\x00\x63\xd4\xb5" \
    "\xb4\x7a\x46\xe5\xe6\x54\xfa\x63\x1d\x61\xfc\x6b" \
    "\xdf\xd0\xe3\x8f\xbf\xe9\x00\x4c\x60\x94\xc8\xd4" \
    "\x97\x67\x44\xde\x40\x48\xc9\x56\xc6\x1d\x1b\x73" \
    "\x85\x71\x74\xfd\x0e\x4a\x42\xfc\x1e\x1c\x5c\xa0" \
    "\x2d\x38\x14\x84\xe4\x11\x88\x31\xcb\x12\x8a\x4d" \
    "\x39\x82\x2a\xfe\x0e\x18\x2e\x70\x5c\xb8\x12\xa2" \
    "\x47\x00\x50\x97\x0a\xc1\x4f\xda\x08\xd9\x17\x4e" \
    "\xa0\x6c\x3a\xdb\xf4\x73\x2d\x02\xc4\x6b\x0a\xf0" \
    "\xed\xa6\x92\x76\xe8\x1b\x2a\x5a\x1e\xa8\x67\x3a" \
    "\x6d\x37\xd7\x2a\x04\x28\x5d\x88\xa9\x36\x8a\xd8" \
    "\x9b\x45\x80\x8b\x9d\x8e\x56\xff\x5a\xe8\xc6\x54" \
    "\x61\x06\xbd\x5a\xdc\x31\xe6\x23\x94\x9c\x41\x1c" \
    "\xc8\xd8\xfc\x43\x27\x87\xe0\xd3\xeb\x56\x6c\x71" \
    "\x9e\xb2\x49\xb8\x4b\x29\xbd\xe7\x86\xe7\xbe\x13" \
    "\x7a\xb5\xc3\x42\xad\x93\x76\x23\xa4\xce\xa3\xb0" \
    "\xb1\x83\x80\x7c\xb3\x42\x88\x08\x12\xf8\x34\x4e" \
    "\xa4\x88\x0d\x04\x38\xa8\x1d\x96\x23\x1f\x2b\x7a" \
    "\x99\xcc\x5a\x66\xf8\x84\xd9\x2a\xa1\xd3\xe0\xa7" \
    "\xae\xa9\x10\x91\xcb\xa2\x54\x6e\x51\xc9\x46\xe6" \
    "\x3f\x6a\x8f\x76\x5d\x9e\x04\x17\xcb\xeb\xad\x5d" \
    "\x2c\xc0\xd9\x04\x84\x6a\x40\x58\x8e\x4a\x9e\x0e" \
    "\x3b\xf7\xbc\xf7\xcf\x93\x09\x21\x94\x19\x4b\x56" \
    "\x81\xe0\x8d\x40\x5d\x09\x80\xa4\xb8\xdf\x7b\x09" \
    "\x07\x9e\x4c\x5a\x90\xfc\x0f\xfa\x7f\x17\xfc\x13" \
    "\xc9\x2f\x4f\xb7\x05\xee\x2c\xf0\x00\x00\x00\x00" \
    "\x49\x45\x4e\x44\xae\x42\x60\x82"
image7_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x02" \
    "\x9d\x49\x44\x41\x54\x38\x8d\xb5\x94\xcf\x4b\x54" \
    "\x51\x14\xc7\x3f\xf7\xcd\xd3\x37\xe9\xcc\xbc\x71" \
    "\x1c\x67\x74\x98\x07\x86\xab\xd2\x7d\x86\xa1\x08" \
    "\x11\x45\x85\x4a\xb4\x70\x27\x4a\x8b\x76\x2d\xfc" \
    "\x0b\x5a\x89\xc8\x20\x48\xb4\x10\x8c\x36\xc2\xa0" \
    "\x50\x38\x20\x04\xa1\x6d\x45\xa8\xb4\x8d\x2e\x02" \
    "\x09\xc2\x18\xc9\x19\xc7\x19\x66\x70\x7c\x9e\x16" \
    "\xf9\x63\x74\x9c\x1f\x15\x1d\x38\x8b\x7b\xdf\xf9" \
    "\x7e\x38\xef\x9e\xef\xbd\x4a\x44\xf8\x1f\xa1\x97" \
    "\xfb\xa8\x94\x52\x40\x2b\xe0\x2e\xd8\xde\x01\x12" \
    "\x22\x92\x2b\xab\x2d\xd5\xb1\x52\xea\xba\x89\xf9" \
    "\x2c\x4f\x7e\xc0\x8b\x57\x74\x74\x01\x70\xe0\x38" \
    "\xc8\x90\xd9\x03\xa2\x71\xe2\x33\x22\xf2\xbd\x6a" \
    "\xb0\x4f\xf9\xee\x1d\x71\xf4\xca\x8f\xdf\x33\xc0" \
    "\x80\xb3\x8b\x2e\x65\x60\x00\x90\x26\xcd\x0a\x2b" \
    "\x32\xc7\x5c\x6e\x97\xdd\x6f\x69\xd2\x8f\x45\xe4" \
    "\x4b\x45\xb0\xa1\x8c\x76\x27\xce\xf7\xbd\xf4\x06" \
    "\x86\x19\xd6\x3c\x78\xd8\x67\x9f\xa7\x3c\x45\x47" \
    "\x67\x8c\x31\x1a\x69\x24\x45\x8a\x69\xa6\x53\x2b" \
    "\xac\xac\x27\x49\xde\x17\x91\xd4\x39\x90\x88\x9c" \
    "\x26\xa0\x9a\x69\x7e\xdd\x41\x47\x2e\x46\x4c\xa2" \
    "\x44\xa5\x8f\xbe\xbd\x20\xc1\x9d\x93\x1a\x13\x33" \
    "\xd9\x49\x67\x36\x4a\x54\xe6\x99\x17\x0b\x6b\x3f" \
    "\x4c\xf8\x49\x21\x47\x44\x8a\xc0\x2d\x6e\xdc\xdb" \
    "\x43\x0c\xc9\x34\xd3\xd2\x45\x57\x36\x48\xf0\x03" \
    "\xf0\x10\xb8\x0a\xb4\xe8\xe8\x77\x5c\xb8\x36\xfb" \
    "\xe9\x4f\x2f\xb3\x2c\x23\x8c\xd8\x7e\xfc\x1f\x01" \
    "\x67\x21\xeb\xa2\x2b\x04\x68\x3c\x5b\x48\x6d\x92" \
    "\xe4\x88\x88\x7c\x2d\xa8\xd9\x76\x28\xc7\x8b\x55" \
    "\x56\x9f\x67\xc9\x62\x61\x69\x1a\x5a\x0b\x50\x03" \
    "\x9c\x3a\xe5\x1c\x58\x44\x7e\x78\x95\xf7\xd3\x02" \
    "\x0b\xfe\x18\x31\x01\xf6\x72\x92\x2b\x84\xa2\x94" \
    "\x6a\x08\x10\xb8\xdb\x46\x5b\xad\x81\xc1\x06\x1b" \
    "\x08\x92\x00\xf2\x85\x75\x45\x3e\x4e\x4a\xf2\xc6" \
    "\xc5\xbd\x93\xa8\x53\x75\x37\x03\x04\x5e\xd6\x50" \
    "\x73\x6d\x90\xc1\xda\x35\xd6\x58\x62\xe9\x40\x47" \
    "\x9f\x2d\xf2\xf5\xc5\x43\x2f\x95\x41\x82\x0f\x4c" \
    "\xcc\x9d\x1e\x7a\xf2\x33\xcc\x48\x84\x88\x84\x08" \
    "\x1d\x58\x58\x6f\x01\x77\xd9\xe1\x95\x4a\x13\xf3" \
    "\xb6\x0f\x5f\xa2\x8f\xbe\xa3\x45\x16\x25\x42\x44" \
    "\x82\x04\xb3\x16\xd6\x9b\xcb\xa0\x55\x81\x01\x67" \
    "\x13\x4d\x9f\xfb\xe9\xcf\x1f\x43\xed\x30\xe1\xbd" \
    "\x10\xa1\xf1\x52\xd0\xcb\x5c\x51\x14\x06\x86\x75" \
    "\xc8\x61\x5b\x37\xdd\x7a\x8e\x1c\x93\x4c\xa6\x33" \
    "\x64\xc6\x12\x24\xc6\x45\xc4\x2e\xa5\xab\x08\x76" \
    "\xe1\xea\xb4\xb1\x6b\x6d\x6c\xd6\x59\x67\x97\x5d" \
    "\x3d\x4d\x3a\x56\x0e\x0a\x65\x1e\xa1\xd3\x8e\x95" \
    "\xd1\x5e\x4f\xfd\xac\x86\x76\x05\x50\x0e\x1c\x5b" \
    "\x71\xe2\x8f\x8a\xae\xf0\x9f\x82\x01\x94\x52\xed" \
    "\x80\xf7\x78\xf9\x53\x44\x36\x2a\x69\x2a\x1e\x85" \
    "\x52\xaa\xd5\xc4\x7c\x67\x63\x37\x00\x38\x70\x24" \
    "\x94\x52\xb7\x44\x64\xeb\x9f\xc0\x80\xc7\xc6\x6e" \
    "\x18\x65\xb4\x0e\x60\x82\x09\x00\x4f\x25\x91\x56" \
    "\x05\xf8\xaf\xa2\x9a\x8e\x53\x1a\xda\xe6\x14\x53" \
    "\xee\xdf\x9d\x68\xfb\x40\xd9\xc1\x41\xf5\xc3\xab" \
    "\xe7\xec\xef\x8e\x44\x24\x53\x49\xf3\x0b\xdf\x5b" \
    "\xae\x1e\x18\x8b\x7a\x54\x00\x00\x00\x00\x49\x45" \
    "\x4e\x44\xae\x42\x60\x82"
image8_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x10\x00\x00\x00\x08" \
    "\x08\x06\x00\x00\x00\xf0\x76\x7f\x97\x00\x00\x00" \
    "\x42\x49\x44\x41\x54\x28\x91\x8d\xd0\xb1\x15\x00" \
    "\x20\x08\x03\xd1\xd3\xc9\x18\x9d\xcd\xb4\x55\x5f" \
    "\x08\xa6\xd5\xfb\x05\xd0\x6f\xb9\xc7\xd9\xc5\x99" \
    "\x69\x91\xf1\x11\x03\x10\x11\xf2\x7f\x05\x5c\xb1" \
    "\x43\x14\x20\xe3\x0a\x79\x01\x1b\x2b\xe4\x04\xec" \
    "\xb5\x8b\xb9\x1b\xfe\x6d\x03\xe1\x83\x16\x45\xa6" \
    "\xee\x58\x99\x00\x00\x00\x00\x49\x45\x4e\x44\xae" \
    "\x42\x60\x82"

class PovrayScenePropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        self.image1 = QPixmap()
        self.image1.loadFromData(image1_data,"PNG")
        self.image3 = QPixmap()
        self.image3.loadFromData(image3_data,"PNG")
        self.image4 = QPixmap()
        self.image4.loadFromData(image4_data,"PNG")
        self.image5 = QPixmap()
        self.image5.loadFromData(image5_data,"PNG")
        self.image6 = QPixmap()
        self.image6.loadFromData(image6_data,"PNG")
        self.image7 = QPixmap()
        self.image7.loadFromData(image7_data,"PNG")
        self.image8 = QPixmap()
        self.image8.loadFromData(image8_data,"PNG")
        self.image2 = QPixmap(image2_data)

        if not name:
            self.setName("PovrayScenePropDialog")

        self.setIcon(self.image0)

        PovrayScenePropDialogLayout = QVBoxLayout(self,0,0,"PovrayScenePropDialogLayout")

        self.heading_frame = QFrame(self,"heading_frame")
        self.heading_frame.setPaletteBackgroundColor(QColor(122,122,122))
        self.heading_frame.setFrameShape(QFrame.NoFrame)
        self.heading_frame.setFrameShadow(QFrame.Plain)
        heading_frameLayout = QHBoxLayout(self.heading_frame,0,3,"heading_frameLayout")

        self.heading_pixmap = QLabel(self.heading_frame,"heading_pixmap")
        self.heading_pixmap.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.heading_pixmap.sizePolicy().hasHeightForWidth()))
        self.heading_pixmap.setPixmap(self.image1)
        self.heading_pixmap.setScaledContents(1)
        self.heading_pixmap.setAlignment(QLabel.AlignVCenter)
        heading_frameLayout.addWidget(self.heading_pixmap)

        self.heading_label = QLabel(self.heading_frame,"heading_label")
        self.heading_label.setPaletteForegroundColor(QColor(255,255,255))
        heading_label_font = QFont(self.heading_label.font())
        heading_label_font.setPointSize(12)
        heading_label_font.setBold(1)
        self.heading_label.setFont(heading_label_font)
        heading_frameLayout.addWidget(self.heading_label)
        PovrayScenePropDialogLayout.addWidget(self.heading_frame)

        self.body_frame = QFrame(self,"body_frame")
        self.body_frame.setFrameShape(QFrame.StyledPanel)
        self.body_frame.setFrameShadow(QFrame.Raised)
        body_frameLayout = QVBoxLayout(self.body_frame,3,3,"body_frameLayout")

        self.sponsor_btn = QPushButton(self.body_frame,"sponsor_btn")
        self.sponsor_btn.setPaletteBackgroundColor(QColor(255,255,255))
        self.sponsor_btn.setPixmap(self.image2)
        self.sponsor_btn.setAutoDefault(0)
        self.sponsor_btn.setFlat(1)
        body_frameLayout.addWidget(self.sponsor_btn)

        layout34 = QHBoxLayout(None,0,6,"layout34")
        left_spacer = QSpacerItem(35,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout34.addItem(left_spacer)

        self.done_btn = QToolButton(self.body_frame,"done_btn")
        self.done_btn.setIconSet(QIconSet(self.image3))
        layout34.addWidget(self.done_btn)

        self.abort_btn = QToolButton(self.body_frame,"abort_btn")
        self.abort_btn.setIconSet(QIconSet(self.image4))
        layout34.addWidget(self.abort_btn)

        self.restore_btn = QToolButton(self.body_frame,"restore_btn")
        self.restore_btn.setIconSet(QIconSet(self.image5))
        layout34.addWidget(self.restore_btn)

        self.preview_btn = QToolButton(self.body_frame,"preview_btn")
        self.preview_btn.setIconSet(QIconSet(self.image6))
        layout34.addWidget(self.preview_btn)

        self.whatsthis_btn = QToolButton(self.body_frame,"whatsthis_btn")
        self.whatsthis_btn.setIconSet(QIconSet(self.image7))
        layout34.addWidget(self.whatsthis_btn)
        right_spacer = QSpacerItem(35,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout34.addItem(right_spacer)
        body_frameLayout.addLayout(layout34)

        self.name_grpbox = QGroupBox(self.body_frame,"name_grpbox")
        self.name_grpbox.setFrameShape(QGroupBox.StyledPanel)
        self.name_grpbox.setFrameShadow(QGroupBox.Sunken)
        self.name_grpbox.setMargin(0)
        self.name_grpbox.setColumnLayout(0,Qt.Vertical)
        self.name_grpbox.layout().setSpacing(1)
        self.name_grpbox.layout().setMargin(4)
        name_grpboxLayout = QVBoxLayout(self.name_grpbox.layout())
        name_grpboxLayout.setAlignment(Qt.AlignTop)

        layout42 = QHBoxLayout(None,0,6,"layout42")

        self.name_grpbox_label = QLabel(self.name_grpbox,"name_grpbox_label")
        self.name_grpbox_label.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Minimum,0,0,self.name_grpbox_label.sizePolicy().hasHeightForWidth()))
        self.name_grpbox_label.setPaletteForegroundColor(QColor(0,0,255))
        self.name_grpbox_label.setAlignment(QLabel.AlignVCenter)
        layout42.addWidget(self.name_grpbox_label)
        spacer21 = QSpacerItem(67,16,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout42.addItem(spacer21)

        self.grpbtn_1 = QPushButton(self.name_grpbox,"grpbtn_1")
        self.grpbtn_1.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.grpbtn_1.sizePolicy().hasHeightForWidth()))
        self.grpbtn_1.setMaximumSize(QSize(16,16))
        self.grpbtn_1.setAutoDefault(0)
        self.grpbtn_1.setIconSet(QIconSet(self.image8))
        self.grpbtn_1.setFlat(1)
        layout42.addWidget(self.grpbtn_1)
        name_grpboxLayout.addLayout(layout42)

        self.line2 = QFrame(self.name_grpbox,"line2")
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.line2.setMidLineWidth(0)
        self.line2.setFrameShape(QFrame.HLine)
        name_grpboxLayout.addWidget(self.line2)

        self.name_linedit = QLineEdit(self.name_grpbox,"name_linedit")
        name_grpboxLayout.addWidget(self.name_linedit)
        body_frameLayout.addWidget(self.name_grpbox)

        self.output_image_grpbox = QGroupBox(self.body_frame,"output_image_grpbox")
        self.output_image_grpbox.setFrameShape(QGroupBox.StyledPanel)
        self.output_image_grpbox.setFrameShadow(QGroupBox.Sunken)
        self.output_image_grpbox.setCheckable(0)
        self.output_image_grpbox.setChecked(0)
        self.output_image_grpbox.setColumnLayout(0,Qt.Vertical)
        self.output_image_grpbox.layout().setSpacing(1)
        self.output_image_grpbox.layout().setMargin(4)
        output_image_grpboxLayout = QVBoxLayout(self.output_image_grpbox.layout())
        output_image_grpboxLayout.setAlignment(Qt.AlignTop)

        layout44 = QHBoxLayout(None,0,6,"layout44")

        self.image_size_grpbox_label = QLabel(self.output_image_grpbox,"image_size_grpbox_label")
        self.image_size_grpbox_label.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Minimum,0,0,self.image_size_grpbox_label.sizePolicy().hasHeightForWidth()))
        self.image_size_grpbox_label.setPaletteForegroundColor(QColor(0,0,255))
        self.image_size_grpbox_label.setAlignment(QLabel.AlignVCenter)
        layout44.addWidget(self.image_size_grpbox_label)
        spacer21_3 = QSpacerItem(40,16,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout44.addItem(spacer21_3)

        self.grpbtn_2 = QPushButton(self.output_image_grpbox,"grpbtn_2")
        self.grpbtn_2.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.grpbtn_2.sizePolicy().hasHeightForWidth()))
        self.grpbtn_2.setMaximumSize(QSize(16,16))
        self.grpbtn_2.setAutoDefault(0)
        self.grpbtn_2.setIconSet(QIconSet(self.image8))
        self.grpbtn_2.setFlat(1)
        layout44.addWidget(self.grpbtn_2)
        output_image_grpboxLayout.addLayout(layout44)

        self.line2_3 = QFrame(self.output_image_grpbox,"line2_3")
        self.line2_3.setFrameShape(QFrame.HLine)
        self.line2_3.setFrameShadow(QFrame.Sunken)
        self.line2_3.setMidLineWidth(0)
        self.line2_3.setFrameShape(QFrame.HLine)
        output_image_grpboxLayout.addWidget(self.line2_3)

        layout16 = QHBoxLayout(None,0,6,"layout16")

        layout15 = QVBoxLayout(None,0,6,"layout15")

        self.image_format_label = QLabel(self.output_image_grpbox,"image_format_label")
        self.image_format_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout15.addWidget(self.image_format_label)

        self.width_label = QLabel(self.output_image_grpbox,"width_label")
        self.width_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout15.addWidget(self.width_label)

        self.height_label = QLabel(self.output_image_grpbox,"height_label")
        self.height_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout15.addWidget(self.height_label)
        layout16.addLayout(layout15)

        layout14 = QVBoxLayout(None,0,6,"layout14")

        self.image_format_combox = QComboBox(0,self.output_image_grpbox,"image_format_combox")
        layout14.addWidget(self.image_format_combox)

        self.width_spinbox = QSpinBox(self.output_image_grpbox,"width_spinbox")
        self.width_spinbox.setMaxValue(5000)
        self.width_spinbox.setMinValue(20)
        self.width_spinbox.setValue(1024)
        layout14.addWidget(self.width_spinbox)

        self.height_spinbox = QSpinBox(self.output_image_grpbox,"height_spinbox")
        self.height_spinbox.setMaxValue(5000)
        self.height_spinbox.setMinValue(20)
        self.height_spinbox.setValue(768)
        layout14.addWidget(self.height_spinbox)
        layout16.addLayout(layout14)
        output_image_grpboxLayout.addLayout(layout16)

        self.maintain_aspect_ratio_checkbox = QCheckBox(self.output_image_grpbox,"maintain_aspect_ratio_checkbox")
        self.maintain_aspect_ratio_checkbox.setChecked(1)
        output_image_grpboxLayout.addWidget(self.maintain_aspect_ratio_checkbox)

        layout57 = QHBoxLayout(None,0,6,"layout57")

        self.aspect_ratio_label = QLabel(self.output_image_grpbox,"aspect_ratio_label")
        self.aspect_ratio_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout57.addWidget(self.aspect_ratio_label)

        self.aspect_ratio_linedit = QLineEdit(self.output_image_grpbox,"aspect_ratio_linedit")
        layout57.addWidget(self.aspect_ratio_linedit)

        self.to_1_label = QLabel(self.output_image_grpbox,"to_1_label")
        layout57.addWidget(self.to_1_label)
        output_image_grpboxLayout.addLayout(layout57)
        body_frameLayout.addWidget(self.output_image_grpbox)
        PovrayScenePropDialogLayout.addWidget(self.body_frame)
        spacer14 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        PovrayScenePropDialogLayout.addItem(spacer14)

        layout42_2 = QHBoxLayout(None,4,6,"layout42_2")
        spacer20 = QSpacerItem(59,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout42_2.addItem(spacer20)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setAutoDefault(0)
        layout42_2.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setAutoDefault(0)
        layout42_2.addWidget(self.ok_btn)
        PovrayScenePropDialogLayout.addLayout(layout42_2)

        self.languageChange()

        self.resize(QSize(229,406).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.aspect_ratio_linedit,SIGNAL("textChanged(const QString&)"),self.aspect_ratio_fixup)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.cancel_btn_clicked)
        self.connect(self.done_btn,SIGNAL("clicked()"),self.ok_btn_clicked)
        self.connect(self.height_spinbox,SIGNAL("valueChanged(int)"),self.change_height)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.ok_btn_clicked)
        self.connect(self.preview_btn,SIGNAL("clicked()"),self.preview_btn_clicked)
        self.connect(self.restore_btn,SIGNAL("clicked()"),self.restore_defaults_btn_clicked)
        self.connect(self.sponsor_btn,SIGNAL("clicked()"),self.open_sponsor_homepage)
        self.connect(self.whatsthis_btn,SIGNAL("clicked()"),self.whatsthis_btn_clicked)
        self.connect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.change_width)
        self.connect(self.abort_btn,SIGNAL("clicked()"),self.cancel_btn_clicked)
        self.connect(self.grpbtn_1,SIGNAL("clicked()"),self.toggle_grpbtn_1)
        self.connect(self.grpbtn_2,SIGNAL("clicked()"),self.toggle_grpbtn_2)


    def languageChange(self):
        self.setCaption(self.__tr("POV-Ray Scene"))
        self.heading_pixmap.setText(QString.null)
        self.heading_label.setText(self.__tr("POV-Ray Scene"))
        self.sponsor_btn.setText(QString.null)
        QWhatsThis.add(self.sponsor_btn,self.__tr("<b>nanoENGINEER-1 Sponsor</b>\n"
"<p>Click on the logo to learn more about this nanoENGINEER-1 sponsor.</p>"))
        self.done_btn.setText(QString.null)
        QToolTip.add(self.done_btn,self.__tr("OK"))
        self.abort_btn.setText(QString.null)
        QToolTip.add(self.abort_btn,self.__tr("Cancel"))
        self.restore_btn.setText(QString.null)
        QToolTip.add(self.restore_btn,self.__tr("Restore Defaults"))
        self.preview_btn.setText(QString.null)
        QToolTip.add(self.preview_btn,self.__tr("Preview"))
        self.whatsthis_btn.setText(QString.null)
        QToolTip.add(self.whatsthis_btn,self.__tr("What's This Help"))
        self.name_grpbox.setTitle(QString.null)
        self.name_grpbox_label.setText(self.__tr("Name"))
        self.grpbtn_1.setText(QString.null)
        self.name_linedit.setText(self.__tr("POV-Ray Scene-1"))
        QToolTip.add(self.name_linedit,self.__tr("Name of POV-Ray Scene"))
        QWhatsThis.add(self.name_linedit,self.__tr("<b>Name</b><p>This field defines the basename for the POV-Ray Scene file.  For example, if the name is <b>POV-Ray Scene-1</b>, the scene file will be named <b>POV-Ray Scene-1.pov</b>.</p>\n"
"<p>The POV-Ray Scene file is placed in the <b>povray</b> directory next to the current part.</p>"))
        self.output_image_grpbox.setTitle(QString.null)
        self.image_size_grpbox_label.setText(self.__tr("Output Image"))
        self.grpbtn_2.setText(QString.null)
        self.image_format_label.setText(self.__tr("Image Format :"))
        self.width_label.setText(self.__tr("Width :"))
        self.height_label.setText(self.__tr("Height :"))
        self.image_format_combox.clear()
        self.image_format_combox.insertItem(self.__tr("PNG"))
        self.image_format_combox.insertItem(self.__tr("BMP"))
        QToolTip.add(self.image_format_combox,self.__tr("Output image format"))
        QWhatsThis.add(self.image_format_combox,self.__tr("<b>Image Format </b>- the output image format when rendering an image from this POV-Ray Scene file."))
        self.width_spinbox.setSuffix(self.__tr(" pixels"))
        QToolTip.add(self.width_spinbox,self.__tr("Width of output image"))
        self.height_spinbox.setSuffix(self.__tr(" pixels"))
        QToolTip.add(self.height_spinbox,self.__tr("Height of output image"))
        self.maintain_aspect_ratio_checkbox.setText(self.__tr("Maintain aspect ratio"))
        QToolTip.add(self.maintain_aspect_ratio_checkbox,self.__tr("Maintain aspect ratio"))
        self.aspect_ratio_label.setText(self.__tr("Aspect Ratio :"))
        self.aspect_ratio_linedit.setText(self.__tr("1.3333"))
        QToolTip.add(self.aspect_ratio_linedit,self.__tr("Aspect ratio of output image"))
        self.to_1_label.setText(self.__tr("to 1"))
        self.cancel_btn.setText(self.__tr("Cancel"))
        QToolTip.add(self.cancel_btn,self.__tr("Cancel"))
        self.ok_btn.setText(self.__tr("OK"))
        QToolTip.add(self.ok_btn,self.__tr("OK"))


    def open_sponsor_homepage(self):
        print "PovrayScenePropDialog.open_sponsor_homepage(): Not implemented yet"

    def ok_btn_clicked(self):
        print "PovrayScenePropDialog.ok_btn_clicked(): Not implemented yet"

    def cancel_btn_clicked(self):
        print "PovrayScenePropDialog.cancel_btn_clicked(): Not implemented yet"

    def preview_btn_clicked(self):
        print "PovrayScenePropDialog.preview_btn_clicked(): Not implemented yet"

    def whatsthis_btn_clicked(self):
        print "PovrayScenePropDialog.whatsthis_btn_clicked(): Not implemented yet"

    def restore_defaults_btn_clicked(self):
        print "PovrayScenePropDialog.restore_defaults_btn_clicked(): Not implemented yet"

    def aspect_ratio_fixup(self):
        print "PovrayScenePropDialog.aspect_ratio_fixup(): Not implemented yet"

    def toggle_grpbtn_1(self):
        print "PovrayScenePropDialog.toggle_grpbtn_1(): Not implemented yet"

    def toggle_grpbtn_2(self):
        print "PovrayScenePropDialog.toggle_grpbtn_2(): Not implemented yet"

    def change_width(self):
        print "PovrayScenePropDialog.change_width(): Not implemented yet"

    def change_height(self):
        print "PovrayScenePropDialog.change_height(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("PovrayScenePropDialog",s,c)
