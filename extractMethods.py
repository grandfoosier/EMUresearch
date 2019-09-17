import sys
import inspect

imports = []
with open(sys.argv[1], "r") as file:
    file_contents = file.readlines()
with open("temp.py", "w") as file:
    for line in file_contents:
        try:
            if line.split(" ")[0] == "import" or line.split()[2] == "import":
                imports += [line.rstrip()]
            else: file.write(line)
        except: file.write(line)
module = __import__("temp")
try:
    members = inspect.getmembers(module, inspect.isfunction)
except TypeError:
    print ('Could not determine module type of %s' % module)

for mem in members:
    fileName = "out/" + sys.argv[1][4:-3] + "_" + mem[0] + ".py"
    with open(fileName, "w") as file:
        for imp in imports: file.write(imp + "\n")
        file.write("\n")
        file.write(inspect.getsource(mem[1]))
