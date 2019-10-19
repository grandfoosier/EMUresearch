import os
import pathlib
import requests
import sys
import threading
import time
import urllib.request

import extractMethods as ex

from bs4 import BeautifulSoup

linkArray = []

def crawlProj(urlIn):
    MAX_THREADS = 50
    LOOP_SLEEP = 0.01

    global linkArray
    linkArray += [urlIn]

    # Single thread version:
    # while linkArray:
    #     urlIn = linkArray[0]; linkArray = linkArray[1:]
    #     openPage(urlIn)
    
    # Multi-thread version:
    while linkArray or threading.active_count() > 1:
        for link in linkArray:
            linkArray.remove(link)
            while threading.active_count() > MAX_THREADS: pass
            thread = threading.Thread(target = openPage, args = (link,))
            thread.start()
        time.sleep(LOOP_SLEEP)

def openPage(urlIn):
    global linkArray
    # Open project page and find all the links
    project = urlIn[urlIn.rfind('/')+1:]
    path = urlIn[18:]
    response = requests.get(urlIn)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all(lambda tag: tag.name == 'a' and
                          tag.get('class') == ['js-navigation-open'])
    for link in links:
        addr = link['href']
        text = link.contents
        # If the link is for a .py file, open the page and copy the file
        if addr[-3:] == ".py": getFile(addr)
        # If the link is for a directory, add it to the linkArray
        elif "/tree/" in addr and ".." not in text:
            linkArray += ["https://github.com"+addr]
    return

def getFile(addr):
    # Remove the "/blob/" from the address
    b = addr.find("/blob/")
    addB = addr[:b]+addr[b+5:]
    # Open the page
    response = requests.get("https://raw.githubusercontent.com"+addB)
    # Make sure the file isn't empty (like some __init__ files)
    if not response.text: return
    s = addB.rfind("/") + 1
    addD = "src"+addB[:s] # directory
    fileName = addB[s:]
    # Make sure the directory exists
    p = pathlib.Path(addD)
    p.mkdir(parents=True, exist_ok=True)
    # Print the filename
    print(str(threading.active_count()) +" "+ addD[4:]+" "+fileName)
    # Copy the file
    with open(addD+fileName, "w", encoding='utf-8') as file:
        file.write(response.text)
    # Extract the functions from the file
    ex.extract(addD+fileName)
    # Delete the source file when done
    os.remove(addD+fileName)
    return

if __name__ == "__main__":
    # run as "python findPyFiles.py url_of_target_project
    crawlProj(sys.argv[1])
