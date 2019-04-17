import sys
import os
import git
import subprocess
import pprint 
from database_handler import DbConnection
import pymongo
import pickle
from timeit import default_timer


path="/Users/saurabdulal/Documents/PROJECTS/STUDY_NETSUS/linux"
os.chdir(path)

netSusSubModules = ["NET: ", "6LOWPAN: ","802: ","8021Q: ","9P: ","KCONFIG: ","MAKEFILE: ","APPLETALK: ",
                    "ATM: ","AX25: ","BATMAN-ADV: ","BLUETOOTH","BPF: ","BPFILTER: ","BRIDGE: ",
                    "CAIF: ","CAN: ","CEPH: ","CORE: ","DCB: ","DCCP: ","DECNET: ",
                    "DNS_RESOLVER: ","DSA: ","ETHERNET: ","HSR: ","IEEE802154: ","IFE: ","IPV4: ",
                    "IPV6: ","IUCV: ","KCM: ","KEY: ","L2TP: ","L3MDEV: ","LAPB: ","LLC: ","MAC80211: ",
                    "MAC802154: ","MPLS: ","NCSI: ","NETFILTER: ","NETLABEL: ","NETLINK: ","NETROM: ",
                    "NFC: ","NSH: ","OPENVSWITCH: ","PACKET: ","PHONET: ","PSAMPLE: ","QRTR: ","RDS: ",
                    "RFKILL: ","ROSE: ","RXRPC: ","SCHED: ","SCTP: ","SMC: ","STRPARSER: ",
                    "SUNRPC: ","SWITCHDEV: ","TIPC: ","TLS: ","UNIX: ","VMW_VSOCK: ",
                    "WIMAX: ","WIRELESS: ","X25: ","XDP: ","XFRM: "]

def dbHandler():
    dbObj = DbConnection();
    database = dbObj.client.netSus
    netSusC = database.netSusC
    # database.netSusC.drop()
    # netSus = database.netSus.create_index([('commitID', pymongo.ASCENDING)], unique=False)
    return netSusC, dbObj

def processModificationStatus(ms):
    # 1 file changed, 8 insertions(+), 23 deletions(-)

    linesAdded = linesDeleted = 0
    fileChanged = ms[0].strip().split(" ")[0]
    try:
        if ms[1] and "insertion" in ms[1]:
            linesAdded = ms[1].strip().split(" ")[0]

        if ms[2] and "deletion" in ms[2]:
            linesDeleted = ms[2].strip().split(" ")[0]

    except Exception as e:
        print(e)
    
    # for debug
    # print(ms,ms[1], fileChanged, linesAdded, linesDeleted)
    return [fileChanged, linesAdded, linesDeleted]

def processCommitMessage(message):
    
    # This function returns back data
    data = None

    if "Merge:" in message:
        return
    subModules = [x for x in netSusSubModules if x in message.upper()]


    #check if no submodules are found and also check if net-drivers are modified
    flagDrivers = False
    if "drivers/net" in message:
        flagDrivers = True

    if not subModules and flagDrivers == False:
        return

    bugFix = False
    
    # check if its a bug fix or feature
    if "FIX" in message.upper():
        bugFix = True

    splittedCommitMessage =  message.split("\n")
    commitId = splittedCommitMessage[0].split(" ")[1]
    author = splittedCommitMessage[1].split(":")[1]
    date = splittedCommitMessage[2].split("Date:")[1].strip()

    subModulesNames = [x.strip() for x in splittedCommitMessage[4].split(":")[:-1]]

    data = {
        "commitID": commitId,
        "author": author,
        "date": date,
        "modificationStatus": processModificationStatus(splittedCommitMessage[len(splittedCommitMessage)-2].split(",")), #how much line, and file is modified
        "subModuleName" : subModulesNames,        
        "isCore" : flagDrivers,                     #is core net or driver 
        "isBugFix" : bugFix}
    
    print(data)

    return data

def processHash(_hash):
    command = "git show "+_hash.strip()+" --stat"
    try:
        proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        comment = out.decode('utf-8').strip()
    except Exception as e:
        print("Could not execute git show command", e)
        
    return processCommitMessage(comment)

def saveDataToDatabase(data):
    pass

def hashTillDate():

    unsavedHash = []
    netSusCol, dbObj = dbHandler()
    # '''
    # in the first pass i was able to get commit through Thu Sep 12 06:11:26 2012 +0200 till 2019
    #date = '2006'
    #command = "git log --date=short --since='April 8 "+date+"' --pretty=format:\"%h%x09%<(20)%an%x09%ad%x09%cd%x09%s\" | awk '{print $1}'"
    
    command = "git log --date=short --since='Thu Jan 12 06:11:26 2006 +0200' --before='Mon Nov 7 21:14:43 2011 +0100' --pretty=format:\"%h%x09%<(20)%an%x09%ad%x09%cd%x09%s\" | awk '{print $1}'"
    
    try:
        proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        hashString = out.decode('utf-8')
    except Exception as e:
        print(e, "Couldn't decode hash string")
        exit(0)

    for _hash in hashString.split():
        data = processHash(_hash.strip("\"").strip()) #just to make sure _hash is clean
        if data:
            try:
                print("Data save:", data, _hash)
                dbObj.insertData(data, netSusCol)
            except Exception as e:
                unsavedHash.append(date['commitID'])
                print(e)

    dbObj.printData(netSusCol)
    with open('unsavedHash.pickle', 'wb') as handle:
        pickle.dump(unsavedHash, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # '''


if __name__ == '__main__':
    # debug input
    # processHash('67022227ffb1f588e70deeccc9246ec93e26f980')
    start = default_timer()
    hashTillDate()
    duration = default_timer() - start
    print("Total execution time: ", duration)
