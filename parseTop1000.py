import findPyFiles as fpf

def scan():
    # Clears the log files. This could be removed if different lists are
    # read in order instead of restarting the one big one.
    with open("paths.txt", "w") as file: pass
    with open("sourcefiles.txt", "w") as file: pass
    with open("exceptions.txt", "w") as file: pass
    # Read the list of 1000 projects
    with open("pythonProjectIndex.txt", "r") as file:
        projects = [line for line in file]
    # Get the address and get the files from Github
    for project in projects:
        l = project.find("https://")
        fpf.crawlProj(project[l: -5])

if __name__ == "__main__":
    scan()
