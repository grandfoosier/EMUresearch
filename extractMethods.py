import ast
import astor
import sys

with open(sys.argv[1]) as file:
    file_contents = file.read()

module = ast.parse(file_contents)

imports = [node for node in module.body if isinstance(node, ast.Import) or
        isinstance(node, ast.ImportFrom)]
importStrs = [astor.to_source(i, indent_with=' ' * 4, add_line_information=False)
        for i in imports]

functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]

for f in functions:
    functionStr = astor.to_source(f, indent_with=' ' * 4, add_line_information=False)

    newName = "out/" + sys.argv[1][4:-3] + "_" + f.name + ".py"
    try:
        with open(newName, "w+") as file:
            for i in importStrs: file.write(i)
            file.write(functionStr)
    except: print("Could not save file " + newName + ".\n")
