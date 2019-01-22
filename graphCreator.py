import itertools
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import datetime
from scipy.sparse import csr_matrix
import networkx as nx
#import matplotlib.pyplot as plt
#from main import vectorMap, entitySetLengthDe
import multiprocessing as mp
import pickle
import pprint

class GraphCreator():
    
    def createVector(self,listOfTuples,length):
        vector = [0]*length
        for tup in listOfTuples:
            vector[tup[0]]=tup[1]
        return np.asarray(vector)
    
    def createSparseMatrix(self,listOfTuples,length):
        zippedTuples = zip(*listOfTuples)
        counter = 0
        counts = np.array([0])
        for w in zippedTuples:
            if counter==0:
                indexes = np.array(list(w))
                counter=counter+1
            elif counter==1:
                counts = np.array(list(w))
                counter=counter+1
            else:
                print("Error while zipping tuples")
        column =[0]*len(indexes)
        return csr_matrix((counts, (indexes, column)), shape=(length, 1))
    
    def hasOverlap(self,listOfTuples1, listOfTuples2):
        bol = False
        zipped1=list(zip(*listOfTuples1))
        zipped2=list(zip(*listOfTuples2))
        if not set(zipped1[0]).isdisjoint(zipped2[0]):
            bol=True
        
        return bol
    
    def createNode(self,graph,node, vector):
        if node in graph:
            return graph
        else: 
            graph.add_node(node,vector=vector)
            return graph
    
    def graphToFile(self,graph,path):
        nx.draw(graph,with_labels=True)
        print("Printed graph to ",path)
        return None
    
    def split(self, a, n):
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))
        
    
    def calculateCosineSim(self,batch, entitySetLength, return_dict):
        for b in batch:
            vectorTuple=batch.get(b)
            v1=self.createSparseMatrix(vectorTuple[0], entitySetLength)
            v2=self.createSparseMatrix(vectorTuple[1], entitySetLength)
            cosineSim = cosine_similarity(v1.reshape(1, -1),v2.reshape(1, -1))
            if cosineSim>0:
                return_dict[b]=cosineSim
            print(b,return_dict[b])
        return True
        
    
    def createGraphParallel(self, vectorMap, entitySetLength):
        print("begin createGraph: ",datetime.datetime.now())
        
        pairsToCaluclate=itertools.combinations(vectorMap, 2)
        print(len(list((pairsToCaluclate)))," pairs to calculate")
        
        actualCalculateMap={}
        for k1, k2 in itertools.combinations(vectorMap, 2):
            if k1!=k2 and vectorMap.get(k1)!=[] and vectorMap.get(k2)!=[] and self.hasOverlap(vectorMap.get(k1), vectorMap.get(k2)):
                actualCalculateMap[(k1,k2)]=(vectorMap.get(k1),vectorMap.get(k2))
        print(len(actualCalculateMap)," with cosineSim > 0")
        print("done with actual calulate map: ",datetime.datetime.now())
        
        with open("actualCalculateMap.dat", "wb") as f:
            pickle.dump(actualCalculateMap, f)

        with open("actualCalculateMap.dat", "rb") as f:
            actualCalculateMap=pickle.load(f)
                
        cores = mp.cpu_count()
        print(cores, " cores available")
        key_batches=list(self.split(list(actualCalculateMap.keys()),cores))
        batches=[]
        for keys in key_batches:
            newMap={}
            for element in keys:
                newMap[element]=actualCalculateMap.get(element)
            batches.append(newMap)
        
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        
        for ba in batches:
            p = mp.Process(target=self.calculateCosineSim, args=(ba,entitySetLength,return_dict))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()
        print("length of return dict",len(return_dict))
        
        with open("/group/project/s1782911/return_dict.dat", "wb") as f:
            pickle.dump(return_dict.copy(), f)
            
          
        with open("/group/project/s1782911/return_dict.dat", "rb") as f:
            return_dict=pickle.load(f)
            print("unpickled")
        
        G=nx.Graph()
        for key, value in return_dict:
            self.createNode(G, key,vectorMap.get(key))
            self.createNode(G, value,vectorMap.get(value))
            if return_dict.get((key,value))[0][0]>0:
                G.add_edge(key, value, weight=return_dict.get((key,value))[0][0] )
                print("created egde between", key, value, return_dict.get((key,value))[0][0])
        print("end createGraph ",datetime.datetime.now())
        return G
    
    
    def createGraph(self,vectorMap,entitySetLength):
        print("begin createGraph: ",datetime.datetime.now())
        print(len(list(itertools.combinations(vectorMap, 2)))," pairs to calculate")
        counter=0
        G=nx.Graph()
        for k1, k2 in itertools.combinations(vectorMap, 2):
            if vectorMap.get(k1)!=[] and vectorMap.get(k2)!=[]:
                self.createNode(G, k1,vectorMap.get(k1))
                self.createNode(G, k2,vectorMap.get(k2))
                if self.hasOverlap(vectorMap.get(k1), vectorMap.get(k2)):
                    v1=self.createSparseMatrix(vectorMap.get(k1), entitySetLength)
                    v2=self.createSparseMatrix(vectorMap.get(k2), entitySetLength)
                    cosineSim = cosine_similarity(v1.reshape(1, -1),v2.reshape(1, -1))
                    if cosineSim>0:
                        G.add_edge(k1, k2, weight=cosineSim )
                    counter=counter+1
        print("end createGraph ",datetime.datetime.now())
        print(counter," pairs calculated")
        return G
        
