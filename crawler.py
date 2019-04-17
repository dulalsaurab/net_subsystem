
'''
@author: Saurab Dulal (sdulal@memphis.edu, The University of Memphis)
This is a python crawler to crawl all the Linux patches released in the last 15 years and get all the patches 
developed for netsubsystem

steps: 
1. get the github URL (https://github.com/torvalds/linux/commits/master)
2. 

'''
# get the dome of this page

from urllib.request import urlopen

from bs4 import BeautifulSoup



baseUrl = 'https://github.com/torvalds/linux/commits/master'
patchPage = "https://github.com/torvalds/linux/commits/master?after=3b04689147085f5c8f47835d1c7e48203cba80d3"

def getCommitPerPage():
    masterDom = BeautifulSoup(urlopen(baseUrl))
    linkDiv = masterDom.findAll("div", {"class": "commit-links-group BtnGroup"})
    commits = []
    for commit in linkDiv:
        commitURL = commit.find_all('a', href=True)
        commits.append(commitURL[0]['href'])
    return commits

def extractPatches(commitsPerPage):
    # loop over each commit and get the page

def storePatch():
    pass

def handler():
    commitURLsPerPage = getCommitPerPage()
    extractPatches(commitURLsPerPage)


if __name__ == '__main__':
    handler()



