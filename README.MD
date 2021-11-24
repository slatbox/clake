# Clake
## Brief Introdunction
Clake is an automatic build to generate clang-makefile(clakefile) from existing makefile.
It will parse the existing makefile firstly and replace gcc and other compile commands with clang commands. It will also replace some incompitible parameters or remvoe some invalid parameters for clang compile system.

## Uasge
~~~ shell
cd project-dir
clake 
~~~

