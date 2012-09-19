### THIS FILE IS NOT YET IN CVS

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.

#e above:
# code for a formula expr, to eval it in an env and object, to a definite value (number or widget or widget expr),
# which no longer depends on env (since nothing in env is symbolic)
# but doing this might well use attrs stored in env or rules/values stored in object, and we track usage of those, for two reasons:
# - the ones in env might change over time
# - the ones in the object might turn out to be general to some class object is in, thus the result might be sharable with others in it.
# so we have eval methods on expr subclasses, with env and object as args, or some similar equiv arg.

