import findPyFiles as fpf

def scan():
    # Clears the log files. This could be removed if different lists are
    # read in order instead of restarting the one big one.
    with open("logs/paths.txt", "w") as file: pass
    with open("logs/sourcefiles.txt", "w") as file: pass
    with open("logs/exceptions.txt", "w") as file: pass
    with open("logs/ex_funcs_short.txt", "w") as file: pass
    with open("logs/ex_files_autogen.txt", "w") as file: pass
    # Read the list of 1000 projects
    with open("pythonProjectIndex.txt", "r") as file:
        projects = [line for line in file]
    # Get the address and get the files from Github
    for project in projects:
        linesplit = project.split()
        projname = linesplit[3][:-4]
        # Make sure the commit hash exists
        projcommit = linesplit[5]
        if len(projcommit) == 40:
            fpf.crawlProj(projname +"/tree/"+ projcommit)

if __name__ == "__main__":
    scan()
