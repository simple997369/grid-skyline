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

    def updateCellSkyline(self):
        pruned = self.window.copy()
        clean = []
        jump = 0
        for  i1 in range(len(pruned)):
            for i2 in range(len(pruned)):
                if i1 == i2:
                    continue
                """two of data gravity in sliding window compare with each other """
                tag = 0
                boundary = 0
                for i3 in range(dim):
                    if pruned[i1][i3+1] <= pruned[i2][i3+1]:
                        tag += 1
                        # break
                    # else:
                    #     break
                    """compare the gravity"""
                if tag != 0:
                    continue
                else:
                    # tag3 = 0
                    # for i3 in range(ps):
                    #     number = pruned[i1][0]*ps + i3
                    #     for i4 in range(dim):
                    #         if alldigits_list[number][i4] > pruned[i2][i4+1]:
                    #             continue
                    #         else:
                    #             tag3 += 1
                    #             break
                    # if tag3 == 0:
                    #     jump += 1
                    #     clean.append(pruned[i1])
                    # """check all instances"""
                    
                    for i3 in range(dim):
                        if pruned[i1][i3+1] - pruned[i2][i3+1] == 1:
                            boundary = 1
                            break
                    """tag the boundary"""
                    if boundary == 0:
                        jump += 1
                        clean.append(pruned[i1])
                    else:
                        # p1min = min(alldigits_list[pruned[i1][0]*ps:pruned[i1][0]*ps+5])
                        # p2max = max(alldigits_list[pruned[i2][0]*ps:pruned[i2][0]*ps+5])
                        tag = 0
                        for i3 in range(dim):
                            for i4 in range(ps):
                                for i5 in range(ps):
                                    if alldigits_list[pruned[i1][0]*ps+i4][i3] > alldigits_list[pruned[i2][0]*ps+i5][i3]:
                                        continue
                                    else:
                                        tag += 1
                                        # break
                            # else:
                            #     break
                        if tag == 0:
                            jump += 1
                            clean.append(pruned[i1])
                        """check all instances"""
                if jump != 0:
                    break
        for i1 in range(len(clean)):
            if clean[i1] in pruned:
                pruned.remove(clean[i1])
        """get the cell skyline"""
        return pruned
    
    def updateSkyline(self,cell_skyline):
        clean = []
        jump = 0
        for i1 in range(len(cell_skyline)):
            for i2 in range(len(cell_skyline)):
                if i1 == i2:
                    continue
                """two of data in cell skyline compare with each other """
                tag = 0
                # """
                for i3 in range(dim):
                    p2 = max([i[i3] for i in dqueue[cell_skyline[i2][0]].locations])
                    for i4 in range(ps):
                        p1 = dqueue[cell_skyline[i1][0]].locations[i4][i3]
                        if p1 > p2:
                            continue
                        else:
                            tag += 1
                            # break
                # """
                # for i3 in range(dim):
                #     p1 = min([i[i3] for i in dqueue[cell_skyline[i1][0]].locations])
                #     p2 = max([i[i3] for i in dqueue[cell_skyline[i2][0]].locations])
                #     if p1 <= p2:
                #         tag += 1
                #         break
                if tag == 0:
                    jump += 1
                    clean.append(cell_skyline[i1])
                    break
            if jump != 0:
                continue
        for i1 in range(len(clean)):
            if clean[i1] in cell_skyline:
                cell_skyline.remove(clean[i1])
        """get the skyline"""
        return cell_skyline

    def showSkyline(self,i,result_pruned):
        #figure show
        plt.subplot(3, 10, i+1 , aspect="equal")
        plt.title(i)
        plt.scatter(result_pruned[:, 1], result_pruned[:, 2], c="r", marker=".", s=30)
        plt.xlim(0,8)
        plt.ylim(0,8)
        
if __name__ == '__main__':

    """
    test code
    """
    count = 10000
    dim = 8
    ps = 5
    wsize = 300
    range_min = 0
    range_max = 1000
    n = 10
    path ='grid-dimension3.txt'
    # path2='z-skyline_grid16.txt'
    # r2= open(path2,'a+')
    r = open(path,'a+')

    dqueue = batchImport('10000_dim8_pos5_rad5_01000.csv', ps)
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

    data = gravityarray
    Min = np.full((1,dim), range_min)
    Max = np.full((1,dim), range_max)
    data = np.append(data , Min , axis=0)
    data = np.append(data , Max , axis=0)
    test = gsp.Grid(data,n)
    digits = test.cell_digits(data)
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
    avgcellsky = 0
    for i in range (count):
        print(i)
        test.receiveData(digits_list[i])
        cell_skyline = test.updateCellSkyline()
        avgcellsky += len(cell_skyline)
        test.updateSkyline(cell_skyline)
        avgsk1 += len(cell_skyline)
        # r2.write("data slot: %s \n" % (i))
        # r2.write("skyline: %s \n" % (cell_skyline))
        # test.showSkyline(i,np.array(cell_skyline))
    avgcellsky = avgcellsky/10000
    avgsk1 = avgsk1/10000
    print('Avg. sky1: '+ str(avgsk1))
    print('avgcellsky:', avgcellsky)
    print("--- %s seconds ---" % (time.time() - start_time))

    r.write("count = {a}  dim = {b}  ps = {c}  wsize = {d}  range_min = {e}  range_max = {f}  grid = {g}\n"
            .format(a=count,b=dim,c=ps,d=wsize,e=range_min,f=range_max,g=n))
    r.write("avgcellsky = {a} \nAvg. sky1 = {b}\n" .format(a=avgcellsky,b=avgsk1))
    r.write("--- %s seconds ---\n" % (time.time() - start_time))
    r.write("-----------\n\n" )

    # plt.tight_layout()
    # plt.show()
                        




    

    


 