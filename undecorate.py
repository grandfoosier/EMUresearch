# Remove the decorator @ from the beginning of functions
# so the tokenizer won't throw an error
def undecorate(func_text):
    if func_text[0] == '@':
        lines = func_text.split("\n")
        untabbed = []
        if lines[0][0] == ' ':
            for line in lines:
                untabbed += [line[4:]]
        elif lines[0][0] == '\t':
            for line in lines:
                untabbed += [line[1:]]
        func_text = '\n'.join(untabbed[1:])
    return func_text
