dup # x # x x
rot # x y z # y z x
drop # x #
over # x y # x y x
swap # x y # y x
pick # n # self->data_stack[self->dspointer-(int)n-1]


eq = # x y # ((double)(x==y))
less < # x y # ((double)(x<y))
lesseq <= # x y # ((double)(x<=y))
greater > # x y # ((double)(x>y))
greatereq >= # x y # ((double)(x>=y))


and # x y # (double)(((int)x)&((int)y))
or # x y # (double)(((int)x)|((int)y))
not # x # (double)(!((int)x))


add + # x y # x+y
sub - # x y # x-y
mul * # x y # x*y
div / # x y # x/y # ASSERT(y != 0);
mod % # x y # x+y # ASSERT(y != 0);


exp ** # x # exp(x)
ln # x # log(x)
pow # x y # exp(y*log(x))
sin # x # sin(x)
cos # x # cos(x)
tan # x # tan(x)


print # x # # printf("%.12f ", x);
println # x # # printf("%.12f\n", x);
newline # # # printf("\n");
ouch # # # PyErr_SetString(IguanaError, "ouch"); return EVILRETURN;
