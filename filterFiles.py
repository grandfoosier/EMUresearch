import re

from tokpystr import tokpystr
from undecorate import undecorate

# Used to separate the functions which would have been excluded from the full
# list made before the filtering
def filterList(name_in, name_out):
    with open(name_in, 'r') as file_in, \
         open(name_out, 'w') as file_out, \
         open('logs/filt_funcs_test.txt', 'w') as file_test, \
         open('logs/filt_funcs_stnd.txt', 'w') as file_stnd:
        for line in file_in:
            # Get just the function name
            left = line.rfind('~') + 1; right = line.find('.py ')
            if left == 0: left = line.rfind('[') + 1
            func_name = line[left: right]
            # Filter out __funcs__
            if exStnd(func_name): file_stnd.write(line)
            # Filter out testFuncs
            elif exTest(line): file_test.write(line)
            # Acceptable methods
            else: file_out.write(line)

# Checks methods based on their names, just stnd and test for now
def exclude(func_name):
    if exStnd(func_name): return True
    if exTest(func_name): return True
    return False

def exStnd(func_name):
    return re.match('__.+__', func_name)
def exTest(func_name):
    # Either test..., stuff_test..., or stuff/test...
    # Others may need to be added.
    return (re.match('.*[/_]test.*', func_name) or
            re.match('\btest.*', func_name))

def ex_by_len(func_text):
    # Remove the @ decorator if it exists
    func_text = undecorate(func_text)
    # Tokenize the code, and return whether there are < 50 of them
    parsed_code = tokpystr(func_text, report_errors=True)
    if len(parsed_code.code_tokens) < 50: return True

if __name__ == '__main__':
    filterList('logs/paths_full.txt', 'logs/paths_filtered.txt')
