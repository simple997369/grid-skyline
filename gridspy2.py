import os, sys
sys.path.append(os.path.abspath(os.pardir))

from data.dataClass import Data, batchImport

import matplotlib.pyplot as plt
import numpy as np
import time
import gridindex as gsp



class gridSKy():
    def __init__(self , dim , wsize , tem_array,dqueue):
        """
        Initializer

        sliding window
        """
        self.skyline1 = np.empty((0, dim+2), int) # sliding window
        self.wsize = wsize # sliding window size
        self.tem_array = tem_array
        self.dqueue = dqueue
        
    def receiveData(self, d):
        """
        Receive one new data.

        :param d: Data
            The received data
        """
        if len(self.skyline1) >= self.wsize:
            self.skyline1 = np.delete( self.skyline1 , 0, axis=0)
        self.skyline1 = np.append(self.skyline1 , [d] , axis=0)

    def updateSkyline(self):
        pruned = self.skyline1.copy()
        pruned2 = np.empty((0,dim+2), int)
        a = np.empty(0,int)

        for  i1 in range(len(pruned)):
            for i2 in range(len(pruned)):
                if i1 == i2:
                    continue
                tag = 0
                for i3 in range(dim):
                    if self.tem_array[pruned[i1][1]][i3] > self.tem_array[pruned[i2][1]][i3]:
                        tag = tag+1
                    else:
                        continue
                if tag == dim :
                    tag = 0
                    for i3 in range(ps):
                        temarray = np.empty(0, int)
                        for i4 in range(dim):
                            temarray = np.append(temarray , dqueue[pruned[i1][1]].__dict__['locations'][i3][i4])
                        temarray = np.array(temarray).reshape(1,dim)
                        temarray = np.append(temarray , Min ,axis=0)
                        temarray = np.append(temarray , Max ,axis=0)
                        test = gsp.Grid(temarray,n)
                        uncertainData = test.cell_id(temarray)
                        uncertainDataGrid = np.where( cell_array == uncertainData[0] )
                        for i4 in range(dim):
                            if uncertainDataGrid[i4][0]>self.tem_array[pruned[i2][1]][i4]:
                                tag = tag + 1
                            else:
                                continue
                if tag == dim*ps:
                    a = np.insert(a , 0 , i1 )
                    pruned2 = np.append( pruned2 , [pruned[i1]] , axis=0 )
                    break
                else:
                    continue
        for i1 in range(len(a)):
            pruned = np.delete(pruned , a[i1] , axis=0)
        
        b = np.empty(0,int)
        for  i1 in range(len(pruned2)):
            for i2 in range(len(pruned2)):
                if i1 == i2:
                    continue
                tag = 0
                for i3 in range(dim):
                    if self.tem_array[pruned2[i1][1]][i3] > self.tem_array[pruned2[i2][1]][i3]:
                        tag = tag+1
                    else:
                        continue
                if tag == dim :
                    tag = 0
                    for i3 in range(ps):
                        temarray = np.empty(0, int)
                        for i4 in range(dim):
                            temarray = np.append(temarray , dqueue[pruned2[i1][1]].__dict__['locations'][i3][i4])
                        temarray = np.array(temarray).reshape(1,dim)
                        temarray = np.append(temarray , Min ,axis=0)
                        temarray = np.append(temarray , Max ,axis=0)
                        test = gsp.Grid(temarray,n)
                        uncertainData = test.cell_id(temarray)
                        uncertainDataGrid = np.where( cell_array == uncertainData[0] )
                        for i4 in range(dim):
                            if uncertainDataGrid[i4][0]>self.tem_array[pruned2[i2][1]][i4]:
                                tag = tag + 1
                            else:
                                continue
                if tag == dim*ps:
                    b = np.insert(b , 0 , i1 )
                    break
                else:
                    continue
        for i1 in range(len(b)):
            pruned2 = np.delete(pruned2 , b[i1] , axis=0)

        return pruned2
        
    def showSkyline(self,i,result_pruned):
        #figure show
        plt.subplot(5, 5, i+1 , aspect="equal")
        plt.title(i)
        plt.scatter(result_pruned[:, 2], result_pruned[:, 3], c="r", marker=".", s=30)
        plt.xlim(0,1000)
        plt.ylim(0,1000)
        
if __name__ == '__main__':

    """
    test code
    """
    count = 25
    dim = 2
    ps = 5
    wsize = 10
    range_min = 0
    range_max = 1000
    n = 32

    dqueue = batchImport('25_dim2_pos5_rad5_01000.csv', ps)
    gravityarray = np.empty((0, dim), int)
    for i in range(count):
        testlist = dqueue[i].__dict__['locations']
        tem = np.empty(0 , int)
        for j in range(dim):  
            temp = 0
            for k in range(ps):
                temp = testlist[k][j] + temp
            tem = np.append(tem , int(temp/ps))
        gravityarray = np.append(gravityarray , [tem] , axis=0)
    data_number = np.arange(count)
    gravityarray = np.c_[ data_number , gravityarray]


    data = gravityarray[: , 1:dim+1]
    Min = np.full((1,dim), range_min)
    Max = np.full((1,dim), range_max)
    data = np.append(data , Min , axis=0)
    data = np.append(data , Max , axis=0)
    test = gsp.Grid(data,n)
    tmp_cellID_array = test.cell_id(data)
    grid_array = np.c_[ tmp_cellID_array[: -2] , gravityarray]
    """ grid_array:[grid_cell_id , point number , dim0 , dim1...] """

    cell_array = np.arange( n**dim ).reshape(n,n)
    tem_array = np.empty((0, dim), int)
    for i in range (count):
        x = np.where( cell_array == tmp_cellID_array[i] )
        tem = np.empty(0 , int)
        for i in range(dim):
            tem = np.append(tem , int(x[i][0]))
        tem_array = np.append(tem_array , [tem] , axis=0)

    plt.figure(0, figsize=(7, 7))
    start_time = time.time()
    test = gridSKy(dim, wsize ,tem_array,dqueue)
    for i in range (count):
        test.receiveData(grid_array[i])
        print(i)
        result_pruned = test.updateSkyline()
        test.showSkyline(i,result_pruned)

    print("--- %s seconds ---" % (time.time() - start_time))


    plt.tight_layout()
    plt.show()



    

    


 