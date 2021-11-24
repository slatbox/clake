from CmdReplacer import *
from MakefileParser import *
import os
import sys

def parseParams():
    params = ""
    for p in sys.argv:
        params += p + " "
    return params
def loadMakefile():
    makefile = None
    if os.path.exists("./Makefile"):
        makefile = Makefile("./Makefile")
    elif os.path.exists("./makefile"):
        makefile = Makefile("./makefile")
    return makefile

def loadRegConf(replacer: CmdReplacer):
    if os.path.exists("./clake-conf.txt"):
        replacer.loadRegFile("./clake-conf.txt")
    elif os.path.exists("/etc/clake/clake-conf.txt"):
        replacer.loadRegFile("/etc/clake/clake-conf.txt")
    else:
        print("No clake-conf.txt found")
        exit(1)
    
if __name__ == '__main__':
    params = parseParams()
    makefile = loadMakefile()
    replacer = CmdReplacer()
    if makefile == None:
        print("Makefile not found.")
        exit(1)
    loadRegConf(replacer)
    makefile.genReplacedFullTextTo(replacer,"./Clakefile")
    os.system("make -f Clakefile " + params)

    
    
