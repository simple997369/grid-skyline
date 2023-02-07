from calendar import c
from copy import copy,deepcopy
import os, sys
from tracemalloc import stop
sys.path.append(os.path.abspath(os.pardir))

import pickle
import time
import numpy as np
import gridindex as gsp
import matplotlib.pyplot as plt
from data.dataClass import Data, batchImport
from zCurve import zCurve as z
here = os.path.dirname(os.path.abspath(__file__))

class gridSKy():
    def __init__(self, count, dim, range_min, range_max, gridcut, wsize, dqueue):
        """
        Initializer

        :param dim: int
            The dimension of data
        :param ps: int
            The occurance count of the instance.
        :param radius: int
            radius use to prevent data being pruned unexpectedly.
            Recommand to be set according to the name of .csv file.
        :param drange: list(int)
            data range [min, max]
        :param wsize: int
            Size of sliding window.
        :param grid_cell_array: array
            grid_array:[grid_cell_id , point number , dim0 , dim1...]
        """
        self.count = count
        self.dim = dim # data dimension
        self.range_min = range_min
        self.range_max = range_max
        self.gridcut = gridcut
        self.ps = ps # possible instance count
        self.window = [] # sliding window
        self.skyline1 = []
        self.wsize = wsize # sliding window size
        self.dqueue = dqueue
        self.outdated = [] # temporary storage for outdated data

    def returnWindow(self):
        return self.window
        
    def receiveData(self, d):
        """
        Receive one new data.

        :param d: Data
            The received data
        """
        if len(self.window) >= self.wsize:
            self.outdated.append(self.window[0])
            del self.window[0]
        self.window.append(d)
        return self.outdated
        
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
                    for i3 in range(dim):
                        if pruned[i1][i3+1] - pruned[i2][i3+1] == 1:
                            boundary = 1
                            break
                    """tag the boundary"""
                    if boundary == 0:
                        jump += 1
                        clean.append(pruned[i1])
                    else:
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
                    for i4 in range(ps):
                        for i5 in range(ps):
                            p1 = dqueue[cell_skyline[i1][0]].locations[i4][i3]
                            p2 = dqueue[cell_skyline[i2][0]].locations[i5][i3]
                            if p1 > p2:
                                continue
                            else:
                                tag += 1
                            # break
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
        self.outdated.clear()
        return cell_skyline

class servergridSky():
    def __init__(self, digits_list, gridsk1, sw,slidingwindow):
        """
        Initializer

        :param dim: int
            The dimension of data
        :param wsize: int
            Size of sliding window.
            Note that the window size should be sum(edge window)
        :param grid_cell_array: array
            grid_array:[grid_cell_id , point number , dim0 , dim1...]
        """
        self.grid_cell_array = digits_list
        self.gridsk1 = gridsk1
        self.wsize = sw
        self.window = slidingwindow

    def receive(self, data):
        """
        Update data received by server

        :param data: dict
            json format(dict) data include change of an edge node.
            Delete: outdated data
            SK1: new data in skyline set
        """
        if len(data[0]['Delete']) > 0:
            for d in data[0]['Delete']:
                if d in self.window:
                    self.window.remove(d)
        if len(data[0]['SK1']) > 0:
            for d in data[0]['SK1']:
                if d not in self.window:
                    self.window.append(d)
        while(len(self.gridsk1) > self.wsize):
            del self.gridsk1[0]

    def update(self):
        pruned = self.gridsk1.copy()
        clean = []
        jump = 0
        for i1 in range(len(pruned)):
            for i2 in range(len(pruned)):
                if i1 == i2:
                    continue
                """two of data in cell skyline compare with each other """
                tag = 0
                # """
                for i3 in range(dim):
                    p2 = max([i[i3] for i in dqueue[cell_skyline[i2][0]].locations])
                    for i4 in range(ps):
                        for i5 in range(ps):
                            p1 = dqueue[cell_skyline[i1][0]].locations[i4][i3]
                            p2 = dqueue[cell_skyline[i2][0]].locations[i5][i3]
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
        skyline = cell_skyline

if __name__ == "__main__":
    rank=(2,4,6,8,10,12,14,16) #edge number
    path ='grid-edge-server-instance.txt'
    r = open(path,'a+')
    for num in rank:
        for ps in (3, 4, 5, 6, 7, 8, 9, 10):#for wsize test
            ### localedge
            edgenum = num
            etmax = []
            print("----- amount of nodes ", edgenum," ------")
            r.write('------ amount of nodes : {a} -------\n'.format(a=edgenum))
            print("instance is",ps)
            r.write('instance is {a} \n'.format(a=ps))
                
            for k in range(edgenum):
                eid = str(k) #edge id
                count = 10000
                dim = 2
                # ps = 5
                range_min = 0
                range_max = 1000
                gridcut = 10
                ew = 300

                dqueue = batchImport('10000_dim2_pos'+str(ps)+'_rad5_01000.csv', ps)
                gravityarray = np.empty((0, dim), int)
                allarray = np.empty((0, dim), int)
                for i in range(count):
                    testlist = dqueue[i].__dict__['locations']
                    allarray = np.append(allarray, testlist ,axis=0)
                    tem = np.empty(0 , int)
                    for j in range(dim):  
                        temp = 0
                        for kk in range(ps):
                            temp = testlist[kk][j] + temp
                        tem = np.append(tem , int(temp/ps))
                    gravityarray = np.append(gravityarray , [tem] , axis=0)

                data = gravityarray
                Min = np.full((1,dim), range_min)
                Max = np.full((1,dim), range_max)
                data = np.append(data , Min , axis=0)
                data = np.append(data , Max , axis=0)
                test = gsp.Grid(data,gridcut)
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

                gridsky = gridSKy(count, dim, range_min, range_max, gridcut, ew, dqueue)

                idx = [i for i in range(count) if i%edgenum == k]
                
                with open('pickle_edge'+eid+'.pickle', 'wb') as f:
                    start_time = time.time()
                    for i in idx:
                        out = gridsky.receiveData(digits_list[i])
                        cell_skyline = gridsky.updateCellSkyline()
                        gridsk1 = gridsky.updateSkyline(cell_skyline)
                        result = {'Delete':out,'SK1':gridsk1}
                        pickle.dump(result, f)

                    finish_time= time.time() - start_time
                    etmax.append(finish_time)
                    print("edge",k+1,"process --- %s seconds ---" % (finish_time))
                    r.write('node number {a} get {b} data process {c} second\n'.format(a=k+1,b=len(idx),c=finish_time))   
                
            r.write('the slowest edge is :{a}\nedge max time is {b}\ntotal edge mean is {c} \n\n'
                        .format(a=(etmax.index(max(etmax))+1),b=max(etmax),c=(sum(etmax)/len(etmax))))
            # exit()
            ### template_picklefile

            
            edgedata =[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
            templist =[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
            for e in range(edgenum):
                idx = [i for i in range(count) if i%edgenum == e]
            
                with open('pickle_edge'+str(e)+'.pickle', 'rb') as f:
                    for d in idx:
                        edgedata[e].append(pickle.load(f))
                        
            templist=deepcopy(edgedata) #for wsize test
            
            ###catch communication load
            
            sdatalist =[]
            r.write('-- Transmission cost with sliding-windows {a}--\n'.format(a=ew))
            for k in range(edgenum):
                sdata =0
                for m in range(len(templist[k])):
                    # print("templist",k,"-",m,templist[k][m])
                    # print("delete len",len(templist[k][m]['Delete']))
                    # print("SK1 len",len(templist[k][m]['SK1']))
                    stemp = len(templist[k][m]['Delete'])+len(templist[k][m]['SK1'])
                    sdata =sdata + stemp
                print("node ", k, "send", sdata) 
                r.write('node {a} send {b}\n'.format(a=k,b=sdata))
                sdatalist.append(sdata)
            print("total transmission", sum(sdatalist))
            r.write('total transmission {a}\n\n'.format(a=sum(sdatalist) ))

            sw = ew*edgenum
            slidingwindow = gridsky.returnWindow()
            gridskyServer = servergridSky(digits_list, gridsk1,sw,slidingwindow)
            server_time = time.time()-time.time() # let time be 0
                                  
            for k in range(count):
                m = k % edgenum # node by node            
                start_time = time.time()
                # print("edge[",m,"]:",edgedata[m])
                gridskyServer.receive(edgedata[m])
                gridskyServer.update()
                t=time.time() - start_time # just calculate the recieve and update time
                server_time = server_time+t
                edgedata[m].pop(0)
                    
                
            print("server-windowsize is",sw)
            print("--- finish --- %s seconds ---" % (server_time))
            
            edgedata =[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]#for wsize test
            edgedata=deepcopy(templist)#for wsize test 
            
                ### write into the file
            r.write('server-windowsize is {a} \n'
                            .format(a=sw))
            r.write('server cost time {a} \n'
                            .format(a=server_time))
            r.write('server+max edge time {a}\n\n'.format(a=server_time+max(etmax)))
            print("Output write into ",path)

    for i in range (16):
        os.remove('./pickle_edge'+str(i)+'.pickle')
