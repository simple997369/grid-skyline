import os, sys
sys.path.append(os.path.abspath(os.pardir))

from data.dataClass import Data, batchImport

import matplotlib.pyplot as plt
import numpy as np
import time
import gridindex as gsp
from zCurve import zCurve as z
import io,csv



class gridSKy():
    def __init__(self ,dim ,ps ,wsize ):
        """
        Initializer

        sliding window
        """
        self.dim = dim # data dimension
        self.ps = ps # possible instance count
        self.wsize = wsize # sliding window size
        # self.window = np.empty((0, dim+1), int) # sliding window
        self.window = []
        
    def receiveData(self, d):
        """
        Receive one new data.

        :param d: Data
            The received data
        """
        if len(self.window) >= self.wsize:
            del self.window[0]
        self.window.append(d)
        
        # if len(self.window) >= self.wsize:
        #     self.window = np.delete( self.window , 0, axis=0)
        # self.window = np.append(self.window , [d] , axis=0)

    def updateSkyline(self):
        pruned = self.window.copy()
        # a = np.empty(0,int)
        clean = []
        for  i1 in range(len(pruned)):
            for i2 in range(len(pruned)):
                if i1 == i2:
                    continue
                """two of data gravity in sliding window compare with each other """
                tag = 0
                tag2 = 0
                for i3 in range(dim):
                    if pruned[i1][i3+1] > pruned[i2][i3+1]:
                        tag += 1
                    else:
                        break
                """compare the gravity"""
                for i3 in range(dim):
                    if pruned[i1][i3+1] - pruned[i2][i3+1] == 1:
                        tag2 = 1
                        break
                """tag the boundary"""
                if tag == dim:
                    tag3 = 0
                    tag4 = 0
                    if tag2 == 0:
                        clean.append(pruned[i1])
                    else:
                        for i3 in range(ps):
                            rest = i3%ps
                            number = pruned[i1][0]*ps + rest
                            for i4 in range(dim):
                                if alldigits_list[number][i4]>pruned[i2][i4+1]:
                                    tag3 += 1
                                    tag4 += 1
                                else:
                                    break
                                # if alldigits_list[number][i4]<=pruned[i2][i4+1]:
                                #     tag3 = 1
                                #     break
                            if tag4 !=0:
                                break
                    if tag3 == dim*ps:
                        clean.append(pruned[i1])
                
        # for i1 in range(len(a)):
        #     pruned = np.delete(pruned , a[i1] , axis=0)
        for i1 in range(len(clean)):
            if clean[i1] in pruned:
                pruned.remove(clean[i1])
        return pruned
        
    def showSkyline(self,i,result_pruned):
        #figure show
        plt.subplot(10, 10, i+1 , aspect="equal")
        plt.title(i)
        plt.scatter(result_pruned[:, 1], result_pruned[:, 2], c="r", marker=".", s=30)
        plt.xlim(0,8)
        plt.ylim(0,8)
        
if __name__ == '__main__':

    """
    test code
    """
    count = 10000
    dim = 2
    ps = 3
    wsize = 300
    range_min = 0
    range_max = 1000
    n = 8
    # path ='z-grid-server.txt'
    # path2='z-skyline_grid16.txt'
    # r = open(path,'a+')
    # r2= open(path2,'a+')

    dqueue = batchImport('10000_dim2_pos3_rad5_01000.csv', ps)
    gravityarray = np.empty((0, dim), int)
    allarray = np.empty((0, dim), int)
    for i in range(count):
        testlist = dqueue[i].__dict__['locations']
        allarray = np.append(allarray, testlist ,axis=0)
        tem = np.empty(0 , int)
        for j in range(dim):  
            temp = 0
            for k in range(ps):
                temp = testlist[k][j] + temp
            tem = np.append(tem , int(temp/ps))
        gravityarray = np.append(gravityarray , [tem] , axis=0)


    data = gravityarray[: , :]
    Min = np.full((1,dim), range_min)
    Max = np.full((1,dim), range_max)
    data = np.append(data , Min , axis=0)
    data = np.append(data , Max , axis=0)
    test = gsp.Grid(data,n)
    digits = test.cell_digits(data)
    data_number = np.arange(count+2)
    # digits = np.c_[ data_number , digits]
    # digits = digits.tolist()
    digits_list = []
    for i in range(count):
        tupletemp = []
        tupletemp.append(i)
        for j in range(dim):
            tupletemp.append(int(digits[i][j])) 
        digits_list.append(tupletemp)

    allarray = np.append(allarray , Min , axis=0)
    allarray = np.append(allarray , Max , axis=0)
    alldigits = test.cell_digits(allarray)
    # alldigits = alldigits.tolist()
    alldigits_list = []
    for i in range(count*ps):
        tupletemp = []
        for j in range(dim):
            tupletemp.append(int(alldigits[i][j])) 
        alldigits_list.append(tupletemp)
    """alldigits: all the instances turn to grid digits"""
    
    # r2.write("---------------count_{a}_dim{b}_pos{c}_wsize{d}_range{e}{f}_gird{g}.csv------------------\n"
    #         .format(a=count,b=dim,c=ps,d=wsize,e=range_min,f=range_max,g=n))

    # plt.figure(0, figsize=(20, 20))
    start_time = time.time()
    test = gridSKy(dim, ps, wsize)
    avgsk1 = 0
    for i in range (count):
        print(i)
        test.receiveData(digits_list[i])
        result_pruned = test.updateSkyline()
        avgsk1 += len(result_pruned)
        # r2.write("data slot: %s \n" % (i))
        # r2.write("skyline: %s \n" % (result_pruned))
        # test.showSkyline(i,np.array(result_pruned))
    avgsk1 = avgsk1/10000
    print('Avg. sky1: '+ str(avgsk1))
    print("--- %s seconds ---" % (time.time() - start_time))

    # r.write("count = {a}\ndim = {b}\nps = {c}\nwsize = {d}\nrange_min = {e}\nrange_max = {f}\nn = {g}\n"
    #         .format(a=count,b=dim,c=ps,d=wsize,e=range_min,f=range_max,g=n))
    # r.write("--- %s seconds ---\n" % (time.time() - start_time))
    # r.write("-----------\n\n" )

    # plt.tight_layout()
    # plt.show()
                     




    

    


 