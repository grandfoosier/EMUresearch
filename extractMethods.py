import pathlib
import inspect
import sys

from libs.redbaron.redbaron import RedBaron

# This will find what classes functions belong to, and will check up to
# one inner class depth
def extract(fileIn):
    # If RedBaron gives an exception, log it and end, otherwise continue
    try:
        with open(fileIn, "r", encoding='utf-8') as file:
            # Read the file and find the class and def nodes
            red = RedBaron(file.read())
            with open("sourcefiles.txt", "a") as file:
                # Add to log
                file.write(fileIn +"\n")
    except:
        with open("exceptions.txt", "a") as file:
            # Add to log
            file.write(fileIn +"\n")
            print("ERROR: "+ fileIn)
            return

    paths = []
    classNodes = red.find_all("classNode")
    nClass = len(classNodes)
    defNodes = red.find_all("defNode")
    nDef = len(defNodes)
    # counters (def, class, class-def, class-class, class-class-def)
    d, c, cd, cc, ccd = 0, 0, 0, 0, 0
    while d < nDef:
        # If you haven't exhausted all the classes yet, you need to check
        # if the next def is in a class
        if c < nClass - 1:
            # Find the classes and defs inside this class
            redC = RedBaron(classNodes[c])
            cClassNodes = redC.find_all("classNode")
            nCClass = len(cClassNodes)
            cDefNodes = redC.find_all("defNode")
            nCDef = len(cDefNodes)
            # If inner classes exist and still need to be checked-
            if cc < nCClass - 1:
                # Find the defs of the inner class
                redCC = RedBaron(cClassNodes[cc+1])
                ccDefNodes = redCC.find_all("defNode")
                nCCDef = len(ccDefNodes)
                # All the defs in this inner class have been checked
                if ccd >= nCCDef:
                    # Iterate the counters
                    cc += 1; ccd = 0
                    continue
                # The next def in this class matches the next overall def
                elif defNodes[d] == ccDefNodes[ccd]:
                    # outclass~inclass~defname
                    defName = (classNodes[c].name + "~" +
                               cClassNodes[cc+1].name + "~" +
                               defNodes[d].name)
                    # Make a file of this function
                    mkfile(paths, fileIn, defNodes[d], defName)
                    # Iterate the counters
                    ccd += 1; cd += 1; d += 1
                    continue
            # All the defs in this class have been checked
            if cd >= nCDef:
                # Iterate the counters
                c +=1; cd = 0; cc = 0; ccd = 0
                continue
            # The next def in this class matches the next overall def
            elif defNodes[d] == cDefNodes[cd]:
                # class~defname
                defName = (classNodes[c].name + "~" +
                           defNodes[d].name)
                # Make a file of this function
                mkfile(paths, fileIn, defNodes[d], defName)
                # Iterate the counters
                cd += 1; d += 1
                continue
        # The next def is not in a class
        defName = defNodes[d].name
        # Make a file of this function
        paths = mkfile(paths, fileIn, defNodes[d], defName)
        # Iterate the counters
        d += 1

    # Add the sorted list of paths to the paths file
    with open("paths.txt", "a", 1) as file:
        for path in sorted(paths): file.write(path)

def mkfile(paths, fileIn, node, defName):
    # Replace src/ with out/ and separate path from filename
    s = fileIn.rfind("/")
    path = "out"+fileIn[3:s]
    fileName = fileIn[s:-3]
    # Make sure the directory exists
    p = pathlib.Path(path)
    p.mkdir(parents=True, exist_ok=True)
    # filename,,class~defname.py
    fileOut = str.format("%s[%s.py" % (fileName, defName))
    # Write the function to the out file
    with open(path + fileOut, "w", encoding='utf-8') as file:
        file.write(node.dumps())
    # Update the paths file
        return paths + ["{0:80s}:  {1:s}/\n".format(fileOut[1:], path)]

if __name__ == "__main__":
    # run as "python extractMethods.py src/name_of_target_file.py"
    # extract(sys.argv[1])
    extract("src/testcode.py")
