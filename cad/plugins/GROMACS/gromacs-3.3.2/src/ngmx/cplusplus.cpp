
// This file is used to force the build into using g++ so our C++ code is
// treated properly.

#include <string>

void foo() { std::string bar = "baz"; }

