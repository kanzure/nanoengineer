"""
Description.py

$Id$

A description is a first-class object whose main purpose is to describe
the structure of another object that could potentially exist or be created.

Specific classes of description can describe specific kinds of objects,
for example, computational processes (or their concrete instantiations),
mathematical objects, sets of configuration settings or preference values,
model database contents, commands or operations that might be done
on specific targets, possible appearances for something graphical, .... ###

Specific classes of description can also help think in certain ways
about the objects they describe, answer questions about them, optimize
them, etc. (E.g. for a description of a process, to be instantiated as
an instance of a target class, some classes of description might use a
simple direct transformation from description structure to process structure,
while others might analyze the process so they can optimize the instances
of it which they create. This is analogous to having compilers of different
quality process the same source code, except that a single object comprises
both the compiler (as description class) and the source code
(as instance-specific data).

This means there can be more than one class of description applicable to
describing any given class of target object. In this case we hope that there
are also transformations between these different description classes. In fact,
providing those is routine, so another way of thinking of this is that a simple
description can be "understood" by transforming it into a complex description,
a.k.a. into an "understanding", of the same target object. Different specialized
understandings can be used for different purposes.

The most concrete operation on a description is to instantiate it, which means,
to create an actual target object which is in fact described accurately by
the description. (Note that this often doesn't fully constrain the target object.
E.g. when compiling the same source code, more than one object program would
count as "correct output" of the compiler.)

Another operation is to transform one description into an equivalent one
(which describes the same set of possible target objects), either of the same
or a different description class (e.g. to "simplify" or "translate" a
description, or more mundanely, to save it in a file or load it from a file).

Instantiation can be thought of as a kind of transformation, but this is not a
precise analogy, since it is allowed to make the description "more specific"
in an irreversible way, by making decisions about things that have to be definite
in any specific instance.

The instantiation function must vary depending on the intended environment and/or
interface for the new instance object.

For an external instantiation function (as opposed to the standard one
provided by the description class, if any), the function has ultimate control
over how to instantiate a particular description; but a typical instantiation
function will let large subclasses of descriptions (which are sufficiently
"tame but general") effectively "instantiate themselves", by calling constructor
methods supplied by the environment in a pattern corresponding to the structure
of the described object (which is often also the structure of the description,
but needn't be in general).

==

Similar things can be said about other kinds of transformations or operations
on descriptions, like copying/saving them, comparing them, or some ways of
analyzing them.

One important but relatively complex kind of transformation on a description
is using the description of some data as "scaffolding for a computation"
which follows the structure of the data but adds arbitrary processing
depending on the data and on its structure. This can be thought of as
transforming a data description into a structurally analogous process
description, which is then instantiated (executed) as it's constructed.
(Note that since the input is a description of data, the output might depend
on which particular description of the same data was used.)

Many processes on complexly structured input data can usefully be expressed
that way; for example:

- the model -> view transformation for a "model tree" or "graphical display"
of structured data (including the offered editing operations as part of the view)

- compiling source code

- handling events from a user interface (the structured input data is the
sequence of user events in time; the messages to event handlers in the
running interactive program are that data's way of describing its own structure
to that program; what the program does can be built on the same structure
(in set-of-objects-space and time) as the input data, but can extend that
as needed with more operations and structure provided by the program). [###CLARIFY]

==

One reason to describe something at a higher level is to avoid bothering its
designers with lower-level details which worsen the complexity burden of
understanding the design. Any higher-level language is an example of that,
whether for programs, user interfaces, math, or anything else.

###
"""


# still to include:
# - description of a process involving changing input data within a structure,
#   and propogation of changes to create changing output data,
#   but optimizing this;
# - a changing description
# - instantiation of changing description => changing target object
#   (a new kind of instantiation, more complex than before)
# - instantation, and its input description, as part of a described process
#   (so a description describes something involving another description);
# - putting all that together, describe the continuous instantiation
#   of a changing description (note that this is no weirder than any other
#   changing application of a complex transformation function)

# applications in this app:
# - descriptions of potential commands, tooltips, highlightpolicies,
#   and state transitions, returned from on_mouse_press_would_do
# - descriptions of graphical appearance of whatevers, as function of their params
# - descriptions of UI structure
# - content of model files (high-level part, above the data tables)
# - description of model data types
#   (note: see StringProperty etc, in Google App Engine)

# maybe: a class is a kind of description, since it knows how to be instantiated.
# but it doesn't necessarily obey the "description api"... maybe we can make some
# classes do that? or wrap any class so it does that?
# similarly, any "constructor function" for an instance might be a kind of description...
# applicable to States for use in Tools...


