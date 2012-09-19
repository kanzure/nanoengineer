# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
povheader.py

@author: Josh
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""

#bruce 050413: moved povpoint from 4 other modules (identical copies) into this one.
# (I'd leave it in fileIO except that would cause a recursive import problem.)
def povpoint(p):
    # note z reversal -- povray is left-handed
    return "<" + str(p[0]) + "," + str(p[1]) + "," + str(-p[2]) + ">"

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

// SkyBlue Gradient colors.
#declare SkyWhite = White * 0.9;
#declare SkyBlue = rgb <.33, .73, 1>;

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

#macro rmotor(p1, p2, rad, col)
  cylinder { p1, p2, rad
   pigment { rgb col }
   finish {Atomic}
   }
#end

#macro lmotor(c1, c2, yrot, xrot, trans, col)
  box { c1,  c2
    rotate yrot
    rotate xrot
    translate trans
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

// macros with hardcoded radii. (since 060622 these might no longer be used)

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

#macro bond(pos1, pos2, col)
  cylinder {pos1, pos2, 0.1
    pigment { rgb col }
    finish {Atomic}
    }
#end

// macros with radius arguments. tube3r is equivalent to drawcylinder. (new as of 060622)

#macro tube1r(rad, pos1, col1, cc1, cc2, pos2, col2)

  cylinder {pos1, cc1, rad
    pigment { rgb col1 }
    finish {Atomic}
    }

  cylinder {cc1, cc2, rad
    pigment { Red }
    finish {Atomic}
    }

  cylinder {cc2, pos2, rad
    pigment { rgb col2 }
    finish {Atomic}
    }

#end

#macro tube2r(rad, pos1, col1, cc1, pos2, col2)

  cylinder {pos1, cc1, rad
    pigment { rgb col1 }
    finish {Atomic}
    }

  cylinder {cc1, pos2, rad
    pigment { rgb col2 }
    finish {Atomic}
    }

#end

#macro tube3r(rad, pos1, pos2, col)

  cylinder {pos1, pos2, rad
    pigment { rgb col }
    finish {Atomic}
    }

#end

#macro bondr(rad, pos1, pos2, col)
  cylinder {pos1, pos2, rad
    pigment { rgb col }
    finish {Atomic}
    }
#end


#macro line(pos1, pos2, col)
  cylinder {pos1, pos2, 0.05
    pigment { rgb col }
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

#macro anchor(pos, rad, col)
  wirebox( pos, rad, col )
#end

#macro stat(pos, rad, col)
  wirebox( pos, rad, col )
#end

#macro thermo(pos, rad, col)
  wirebox( pos, rad, col )
#end

#macro gamess(pos, rad, col)
  wirebox( pos, rad, col )
#end

#macro esp_plane_texture(p1, p2, p3, p4, imgName)
    mesh2 {
      vertex_vectors
      {
        4,
        p1, p2, p3, p4
      }
      uv_vectors {
        4,
        <0.0, 1.0>, <0.0, 0.0>,
        <1.0, 0.0>, <1.0, 1.0>
      }
      face_indices
      {
        2,
        <0, 1, 2>,
        <0, 2, 3>
      }
      uv_mapping
      pigment { image_map {png imgName
                          }
      }
      finish {Atomic}
    }
#end

#macro esp_plane_color(p1, p2, p3, p4, col4)
    mesh2 {
      vertex_vectors
      {
        4,
        p1, p2, p3, p4
      }
      face_indices
      {
        2,
        <0, 1, 2>,
        <0, 2, 3>
      }
      pigment {rgbf col4}
      finish {Atomic}
    }
#end

#macro grid_plane(p1, p2, p3, p4, col)
    cylinder { p1,  p2, 0.05
          pigment { rgb col }
          finish {Atomic}
    }
    cylinder { p2,  p3, 0.05
          pigment { rgb col }
          finish {Atomic}
    }
    cylinder { p3,  p4, 0.05
          pigment { rgb col }
          finish {Atomic}
    }
    cylinder { p4,  p1, 0.05
          pigment { rgb col }
          finish {Atomic}
    }
#end

#macro Rotate_X(Axis, Angle)
   #local vX = vaxis_rotate(x,Axis,Angle);
   #local vY = vaxis_rotate(y,Axis,0);
   #local vZ = vaxis_rotate(z,Axis,0);
   transform {
      matrix < vX.x,vX.y,vX.z, vY.x,vY.y,vY.z, vZ.x,vZ.y,vZ.z, 0,0,0 >
   }
#end

"""
