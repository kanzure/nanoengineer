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

#declare Gray10 = White * 0.9;
#declare Gray25 = White  *0.75;
#declare Gray40 = White  *0.60;
#declare Gray50 = White * 0.50;
#declare Gray75 = White * 0.25;

// LIGHTBULB: for debugging light sources for POV-Ray images - Mark
#declare Lightbulb = union {
    merge {
      sphere { <0,0,0>,1 }
      cylinder {
        <0,0,1>, <0,0,0>, 1
        scale <0.35, 0.35, 1.0>
        translate  0.5*z
      }
      texture {
        pigment {color rgb <1, 1, 1>}
        finish {ambient .8 diffuse .6}
      }
    }
    cylinder {
      <0,0,1>, <0,0,0>, 1
      scale <0.4, 0.4, 0.5>
      translate  1.5*z
    }
    rotate -90*x
    scale .5
}
  
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

#macro tube3(pos1, pos2, col)

  cylinder {pos1, pos2, 0.3
    pigment { rgb col }
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

#macro wirebox(pos, rad, col)
#declare  c1 = pos - rad;
#declare  c2 = pos - <-rad,rad,rad>;
#declare  c3 = pos - <-rad,-rad,rad>;
#declare  c4 = pos - <rad,-rad,rad>;
#declare  c5 = pos + <-rad,-rad,rad>;
#declare  c6 = pos + <rad,-rad,rad>;
#declare  c7 = pos + rad;
#declare  c8 = pos + <-rad,rad,rad>;
  cylinder { c1,  c2, 0.05
    pigment { rgb col }
    finish {Atomic}    
    }
  cylinder { c2,  c3, 0.05
    pigment { rgb col }
    finish {Atomic}    
    }
  cylinder { c3,  c4, 0.05
    pigment { rgb col }
    finish {Atomic}    
    }
  cylinder { c4,  c1, 0.05
    pigment { rgb col }
    finish {Atomic}    
    }
  cylinder { c5,  c6, 0.05
    pigment { rgb col }
    finish {Atomic}    
    }
  cylinder { c6,  c7, 0.05
    pigment { rgb col }
    finish {Atomic}    
    }
  cylinder { c7,  c8, 0.05
    pigment { rgb col }
    finish {Atomic}    
    }
  cylinder { c8,  c5, 0.05
    pigment { rgb col }
    finish {Atomic}    
    }
  cylinder { c1,  c5, 0.05
    pigment { rgb col }
    finish {Atomic}    
    }
  cylinder { c2,  c6, 0.05
    pigment { rgb col }
    finish {Atomic}    
    }
  cylinder { c3,  c7, 0.05
    pigment { rgb col }
    finish {Atomic}    
    }
  cylinder { c4,  c8, 0.05
    pigment { rgb col }
    finish {Atomic}    
    }
#end

#macro ground(pos, rad, col)
  wirebox( pos, rad, col )
#end

#macro stat(pos, rad, col)
  wirebox( pos, rad, col )
#end

"""