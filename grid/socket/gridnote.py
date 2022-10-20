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
        self.window = np.empty((0, self.dim+2), int) # sliding window
        self.skyline1 = np.empty((0, self.dim+2), int) 
        self.wsize = wsize # sliding window size
        self.dqueue = dqueue
        self.outdated = np.empty((0, self.dim+2), int) # temporary storage for outdated data
        self.gravityarray = np.empty((0, self.dim), int)
        self.grid_array = np.empty((0, self.dim+2), int)
        self.grid_cell_array = np.empty((0, self.dim), int)

    def turngravity(self):
        temp_gravityarray = np.empty((0, self.dim), int)
        for i in range(self.count):
            testlist = self.dqueue[i].__dict__['locations']
            tem = np.empty(0 , int)
            for j in range(self.dim):  
                temp = 0
                for i3 in range(self.ps):
                    temp = testlist[i3][j] + temp
                tem = np.append(tem , int(temp/self.ps))
            temp_gravityarray = np.append(temp_gravityarray , [tem] , axis=0)
        data_number = np.arange(self.count)
        self.gravityarray = np.c_[ data_number , temp_gravityarray ]
        return self.gravityarray

    def turngrid(self, d):
        data = d[: , 1:self.dim+1]
        self.Min = np.full((1,self.dim), self.range_min)
        self.Max = np.full((1,self.dim), self.range_max)
        data = np.append(data , self.Min , axis=0)
        data = np.append(data , self.Max , axis=0)
        test = gsp.Grid(data, self.gridcut)
        self.tmp_cellID_array = test.cell_id(data)
        self.grid_array = np.c_[ self.tmp_cellID_array[: -2] , self.gravityarray]
        return self.grid_array 

    def turngridcell(self):
        self.cell_array = np.arange(self.gridcut**self.dim ).reshape(self.gridcut,self.gridcut)
        tem_array = np.empty((0, self.dim), int)
        for i in range (self.count):
            x = np.where( self.cell_array == self.tmp_cellID_array[i] )
            tem = np.empty(0 , int)
            for j in range(self.dim):
                tem = np.append(tem , int(x[j][0]))
            tem_array = np.append(tem_array , [tem] , axis=0)
        self.grid_cell_array = tem_array
        return self.grid_cell_array
        
    def receiveData(self, d):
        """
        Receive one new data.

        :param d: Data
            The received data
        """
        if len(self.window) >= self.wsize:
            self.outdated = np.append(self.outdated , [self.window[0]] , axis=0)
            self.window = np.delete( self.window , 0, axis=0)
        self.window = np.append(self.window , [d] , axis=0)
        return self.outdated
        
    def updateSkyline(self):
        pruned = self.window.copy()
        a = np.empty(0,int)
        for  i1 in range(len(pruned)):
            for i2 in range(len(pruned)):
                if i1 == i2:
                    continue
                tag = 0
                for i3 in range(self.dim):
                    if self.grid_cell_array[pruned[i1][1]][i3] > self.grid_cell_array[pruned[i2][1]][i3]:
                        tag = tag+1
                    else:
                        continue
                if tag == self.dim :
                    tag = 0
                    for i3 in range(self.ps):
                        temarray = np.empty(0, int)
                        for i4 in range(self.dim):
                            temarray = np.append(temarray , dqueue[pruned[i1][1]].__dict__['locations'][i3][i4])
                        temarray = np.array(temarray).reshape(1,dim)
                        temarray = np.append(temarray , self.Min ,axis=0)
                        temarray = np.append(temarray , self.Max ,axis=0)
                        test = gsp.Grid(temarray,self.gridcut)
                        uncertainData = test.cell_id(temarray)
                        uncertainDataGrid = np.where( self.cell_array == uncertainData[0] )
                        for i4 in range(dim):
                            if uncertainDataGrid[i4][0]>self.grid_cell_array[pruned[i2][1]][i4]:
                                tag = tag + 1
                            else:
                                continue
                if tag == dim*ps:
                    a = np.insert(a , 0 , i1 )
                    break
                else:
                    continue
        for i1 in range(len(a)):
            pruned = np.delete(pruned , a[i1] , axis=0)

        self.skyline1 = pruned
        return self.skyline1

class servergridSky():
    def __init__(self, grid_cell_array, gridsk1):
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
        self.grid_cell_array = grid_cell_array
        self.gridsk1 = gridsk1
    def receive(self, data):
        """
        Update data received by server

        :param data: dict
            json format(dict) data include change of an edge node.
            Delete: outdated data
            SK1: new data in skyline set
        """
        # print(data[0])
        if len(data[0]['Delete']) > 0:
            for d in data[0]['Delete']:
                sk1_id = np.where(d[1] == self.gridsk1)
                if sk1_id[1][0] == 1:
                    self.gridsk1 = np.delete( self.gridsk1 , sk1_id[0][0], axis=0)
        if len(data[0]['SK1']) > 0:
            for d in data[0]['SK1']:
                sk1_id = np.where(d[1] == self.gridsk1)
                if np.size(sk1_id[0]) == 0:
                    self.gridsk1 = np.append(self.gridsk1 , [d] , axis=0)

    def update(self):
        pruned = self.gridsk1.copy()
        a = np.empty(0,int)
        for  i1 in range(len(pruned)):
            for i2 in range(len(pruned)):
                if i1 == i2:
                    continue
                tag = 0
                for i3 in range(dim):
                    if self.grid_cell_array[pruned[i1][1]][i3] > self.grid_cell_array[pruned[i2][1]][i3]:
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
                        temarray = np.append(temarray , gridsky.Min ,axis=0)
                        temarray = np.append(temarray , gridsky.Max ,axis=0)
                        test = gsp.Grid(temarray,gridcut)
                        uncertainData = test.cell_id(temarray)
                        uncertainDataGrid = np.where( gridsky.cell_array == uncertainData[0] )
                        for i4 in range(dim):
                            if uncertainDataGrid[i4][0]>self.grid_cell_array[pruned[i2][1]][i4]:
                                tag = tag + 1
                            else:
                                continue
                if tag == dim*ps:
                    a = np.insert(a , 0 , i1 )
                    break
                else:
                    continue
        for i1 in range(len(a)):
            pruned = np.delete(pruned , a[i1] , axis=0)

        self.outdated = np.empty((0, dim+2), int)
        self.skyline1 = pruned

if __name__ == "__main__":
    rank=(2,4,6,8,10,12,14,16) #edge number
    path ='grid-edge-server-winsize.txt'
    r = open(path,'a+')
    for num in rank:
        for ew in (100,300,500,700):#for wsize test
            ### localedge
            edgenum = num
            etmax = []
            print("----- amount of nodes ", edgenum," ------")
            r.write('------ amount of nodes : {a} -------\n'.format(a=edgenum))
            print("edge-windowsize is",ew)
            r.write('edge-windowsize is {a} \n'
                            .format(a=ew))
                
            for k in range(edgenum):
                eid = str(k) #edge id
                count = 25
                dim = 2
                ps = 5
                range_min = 0
                range_max = 1000
                gridcut = 32

                dqueue = batchImport('25_dim2_pos5_rad5_01000.csv', ps)
                gridsky = gridSKy(count, dim, range_min, range_max, gridcut, ew, dqueue)

                gravityarray = gridsky.turngravity()
                grid_array = gridsky.turngrid(gravityarray)
                grid_cell_array = gridsky.turngridcell()

                idx = [i for i in range(count) if i%edgenum == k]
                
                with open('pickle_edge'+eid+'.pickle', 'wb') as f:
                    start_time = time.time()
                    for i in idx:
                        print(i)
                        out = gridsky.receiveData(grid_array[i])
                        gridsk1 = gridsky.updateSkyline()
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
            gridskyServer = servergridSky(grid_cell_array, gridsk1)
            server_time = time.time()-time.time() # let time be 0
                                  
            for k in range(count):
                m = k % edgenum # node by node            
                start_time = time.time()
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
            
    os.remove('./pickle_edge0.pickle')
    os.remove('./pickle_edge1.pickle')
    os.remove('./pickle_edge2.pickle')
    os.remove('./pickle_edge3.pickle')