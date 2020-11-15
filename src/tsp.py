#!/usr/bin/env python
import numpy as np
def calc_path(start_coord, path):
    way=[];
    X = []
    Y = []
    a=0
    for item in path:
        X.append(item[0])
        Y.append(item[1])
        if item == start_coord:
            start = path.index(item)
    n=len(X)
    M = np.zeros([n,n])
    for i in np.arange(0,n,1):
             for j in np.arange(0,n,1):
                      if i!=j:
                               M[i,j]=np.sqrt((X[i]-X[j])**2+(Y[i]-Y[j])**2)
                      else:
                               M[i,j]=float('inf')         
    way.append(start)
    for i in np.arange(1, n, 1):
             s=[]
             for j in np.arange(0, n, 1):                  
                      s.append(M[way[i-1], j])
             way.append(s.index(min(s)))
             for j in np.arange(0,i,1):
                      M[way[i],way[j]]=float('inf')
                      M[way[i],way[j]]=float('inf')
    S=sum([np.sqrt((X[way[i]]-X[way[i+1]])**2+(Y[way[i]]-Y[way[i+1]])**2) for i in np.arange(0,n-1,1)])+ np.sqrt((X[way[n-1]]-X[way[0]])**2+(Y[way[n-1]]-Y[way[0]])**2)                      
    return way
