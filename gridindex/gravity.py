import attr
import numpy as np
import validators as vlds
import os, sys
sys.path.append(os.path.abspath(os.pardir))
from data.dataClass import Data, batchImport


if __name__ == '__main__':
    dqueue = batchImport('30_dim5_pos5_rad5_01000.csv',5)
    gravityarray = np.empty((0, 5), int) #dim
    for i in range(30):
        testlist = dqueue[i].__dict__['locations']
        print(testlist)
        tem = np.empty(0 , int)
        for j in range(5):  #ps
            temp = 0
            for k in range(5):
                temp = testlist[k][j] + temp
            tem = np.append(tem , int(temp/5))
        gravityarray = np.append(gravityarray , [tem] , axis=0)    
    print(gravityarray)



    