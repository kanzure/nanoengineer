# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
__author__ = "Josh"

povheader = """
// COLORS:
#declare Red     = rgb <1, 0, 0>;
#declare Green   = rgb <0, 1, 0>;
#declare Blue    = rgb <0, 0, 1>;
#declare Yellow  = rgb <1,1,0>;
#declare Cyan    = rgb <0, 1, 1>;
#declare Magenta = rgb <1, 0, 1>;
#declare Clear   = rgbf 1;
#declare White   = rgb 1;
#declare Black   = rgb 0;

#declare Gray25 = White*0.25;
#declare Gray50 = White*0.50;
#declare Gray75 = White*0.75;


#declare Atomic =
finish {
    ambient 0.4
    diffuse 1.0
    phong 0.3
}

#macro rmotor(p1, p2, rad, col)
  cylinder { p1, p2, rad
   pigment { rgb col }
   finish {Atomic}
   }
#end

#macro lmotor(p1, p2, w, col) 
  box { p1 + w,  p2 - w
    pigment { rgb col }
    finish {Atomic}
    }
#end
  
#macro spoke(p1, p2, rad, col)
  cylinder { p1, p2, rad
   pigment { rgb col }
   finish {Atomic}
   }
#end

#macro ground(pos, rad, col) 
  box { pos - rad*0.95,  pos + rad*0.95
    pigment { rgb col }
    finish {Atomic}
    }
#end

#macro stat(pos, rad, col) 
  box { pos - rad*0.95,  pos + rad*0.95
    pigment { rgb col }
    finish {Atomic}
    }
#end
  
#macro atom(pos, rad, col) 
  sphere { pos, rad
    pigment { rgb col }
    finish {Atomic}
    }
#end

#macro tube1(pos1, col1, cc1, cc2, pos2, col2)

  cylinder {pos1, cc1, 0.3
    pigment { rgb col1 }
    finish {Atomic}
    }

  cylinder {cc1, cc2, 0.3
    pigment { Red }
    finish {Atomic}
    }

  cylinder {cc2, pos2, 0.3
    pigment { rgb col2 }
    finish {Atomic}
    }
    
#end

#macro tube2(pos1, col1, cc1, pos2, col2)

  cylinder {pos1, cc1, 0.3
    pigment { rgb col1 }
    finish {Atomic}
    }

  cylinder {cc1, pos2, 0.3
    pigment { rgb col2 }
    finish {Atomic}
    }
    
#end

#macro bond(pos1, pos2) 
  cylinder {pos1, pos2, 0.1
    pigment { Gray75 }
    finish {Atomic}
    }
#end

#macro line(pos1, pos2) 
  cylinder {pos1, pos2, 0.05
    pigment { Black }
    }
#end

"""