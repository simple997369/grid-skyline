# Sliding window update PSky
import os, sys
from pickle import EMPTY_LIST
sys.path.append(os.path.abspath(os.pardir))

import time

skylinelist = []

#test data
entry1 = [11,1,1] # [sequenceID, objectpoint, itemtag 1:EX ; 0:SK]
entry2 = [11,2,0]
entry3 = [11,3,0]
entry4 = [11,6,0]
eventlist = [entry1,entry2,entry3,entry4]


currenttime = time.time()
def procExpiration():
    if len(eventlist) == 0:
        print('list is empty')
    else:
        if eventlist[0][2] == 1:  #itemtag in entry1
            eventlist.pop(0)
        else:
            eventlist[0][2] = 1   #還要處理timestamp&influence time&window side的問題
            skylinelist.append(eventlist[0])
            eventlist.pop(0)
            eventlist.append(skylinelist[-1])
        print("sl:", skylinelist)
        print("el:", eventlist)

        
if __name__ == '__main__':
   # while len(eventlist)!=0 :
    for i in range(len(eventlist)):
        procExpiration()
    
