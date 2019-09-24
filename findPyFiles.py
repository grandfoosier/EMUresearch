import pathlib
import requests
import sys
import urllib.request

from bs4 import BeautifulSoup

import extractMethods as ex

def openPage(urlIn):
    project = urlIn[urlIn.rfind('/')+1:]
    path = urlIn[18:]
    response = requests.get(urlIn)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all(lambda tag: tag.name == 'a' and
                                   tag.get('class') == ['js-navigation-open'])
    for link in links:
        addr = link['href']
        text = link.contents
        if ".py" in addr:
            b = addr.find("/blob")
            addB = addr[:b]+addr[b+5:]
            response = requests.get("https://raw.githubusercontent.com"+addB)
            if response.text:
                m = addB.find("/master")
                s = addB.rfind("/")
                addD = "src"+addB[:m]+addB[m+7:s]
                fileName = addB[s:]
                p = pathlib.Path(addD)
                p.mkdir(parents=True, exist_ok=True)
                input(addD+" "+fileName)
                with open(addD+fileName, "w") as file:
                    file.write(response.text)
                ex.extract(addD+fileName)
        elif "tree/master" in addr and ".." not in text:
            openPage("https://github.com"+addr)

if __name__ == "__main__":
    # run as "python findPyFiles.py url_of_target_project
    # openPage(sys.argv[1])
    openPage("https://github.com/donnemartin/system-design-primer")
