// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*----------------------------------------------------------------------------

Copyright (c) 2000, Brad Grantham and Applied Conjecture. All
rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
  3. Neither the name Brad Grantham nor Applied Conjecture
     may be used to endorse or promote products derived from this software
     without permission.

THIS SOFTWARE IS PROVIDED BY BRAD GRANTHAM AND APPLIED CONJECTURE``AS
IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE BRAD GRANTHAM
OR APPLIED CONJECTURE BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

----------------------------------------------------------------------------*/

#ifndef _vector_h_
#define _vector_h_

#ifdef _WIN32
#ifndef M_PI
#define M_PI 3.14159265
#endif /* M_PI */
#endif /* WIN32 */


#ifdef __cplusplus
extern "C" {
#endif

float vec3fDot(float v0[3], float v1[3]);
void vec3fBlend(float v0[3], float w0, float v1[3], float w1, float result[3]);
void vec3fScale(float v[3], float w, float r[3]);
float vec3fLength(float v[3]);
void vec3fNormalize(float v[3], float r[3]);
void vec4fCopy(float src[4], float dest[4]);
void mat4fMultVec3fPt(float m[16], float in[3], float out[3]);
float mat4fDeterminant(float mat[16]);
int mat4fInvert(float mat[16], float inv[16]);

#ifdef __cplusplus
}
#endif

#endif /* _vector_h_ */
