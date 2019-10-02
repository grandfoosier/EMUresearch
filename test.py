from redbaron import RedBaron
def main():
    with open("testcode.py", "r") as source_code:
        red = RedBaron(source_code.read())
        # print(red.help()) ## try this to see the data structure of 'red'
        defNodes = red.find_all('DefNode');
        # print(defNode.help()) ## try this to see the data structure of 'defNode'
        for defNode in defNodes: print(defNode.help())


if __name__ == "__main__":
    main()
